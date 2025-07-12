from threading import Thread, Timer
import time
from flask import current_app
from app.extensions import socketio
from app.sockets.helpers import create_and_fund_players, create_player_object, get_user_bankroll, update_player_chips, delete_game, cashout_player, remove_user_from_game
from app.game_logic.game_logic import PokerRound
from app.timer.inaction_timer import InactionTimer
import app.state as state
from app.globals import StatusEnum

def emit_player_turn(game_id: str, delay=45):
    game = state.get_game(game_id)
    data = game.get_player_to_act_and_actions() # {"player_to_act": Player, "actions": [{"action": , "min": , "allin": }, {}]}
    socketio.emit("player_turn", data, to=game_id)
    kick_player_after_delay(current_app._get_current_object(), game_id, data["player_to_act"], delay=delay)

def kick_player_after_delay(app, game_id: str, username: str, delay: int=30):
    def kick_player(game_id: str, username: str):
        state.append_to_leaver_queue(game_id, username)
        handle_player_action_helper(username, game_id, "fold", None)

    timer = InactionTimer(socketio, app, game_id, username, delay, state.get_game, kick_player) # Timer(delay, kick_player, [game_id, username])
    state.set_player_timer(game_id, username, timer)
    print("set player timer", state.get_player_timer(game_id, username), f"for {username}")    
    timer.start()

def emit_updated_game_state(game: PokerRound):
    for name in game.get_players():
        game_state = game.serialize_for_player(name)
        socketio.emit("update_game_state", game_state, to=name)

def emit_round_over(game_id: str):
    game = state.get_game(game_id)
    pot_award_info = game.end_poker_round() # [{"winners": list[str], "amount": int, "share": int}, {...}]
    emit_updated_game_state(game) # additional update to show newly dealt cards if needed
    socketio.emit("round_over", pot_award_info, to=game_id)
    return pot_award_info

def emit_revealed_hands(game_id: str, pot_award_info: dict):
    must_show_players = state.get_game(game_id).determine_must_show_players(pot_award_info)
    for entry in must_show_players:
        socketio.emit("hand_revealed", entry, to=game_id)

def cleanup_leavers(game_id: str):
    if state.get_host(game_id) in state.get_leaver_queue(game_id):
        socketio.emit("message", "Game host removed - assigning new host.", to=game_id)
        print(state.get_players(game_id))
        print(state.get_leaver_queue(game_id))
        eligible_players = set(state.get_players(game_id)).difference(set(state.get_leaver_queue(game_id)))
        print(eligible_players)
        if not eligible_players:
            socketio.emit("error", {"message": "No one was eligible to be the next host."})
            delete_game(game_id)
            return False
        else:
            state.set_host(game_id, eligible_players.pop())
            print(f"setting new host as {state.get_host(game_id)}")

    for username in state.get_leaver_queue(game_id)[:]:
        print(f"removing {username} from {game_id}")
        cashout_player(state.get_game(game_id), username)
        remove_user_from_game(game_id, username)
        socketio.emit("chips_updated", to=username)
        socketio.emit("player_removed", game_id, to=username)

    return True

def cleanup_joiners(game_id: str):
    for username in state.get_joiner_queue(game_id)[:]:
        # TODO ensure table does not exceed seat limit
        update_player_chips(username, get_user_bankroll(username) - state.get_buy_in(game_id))
        state.get_game(game_id).add_player(create_player_object(username, state.get_buy_in(game_id)))
        state.append_to_players(game_id, username)
        socketio.emit("player_joined", {"game_id": game_id, "username": username})  # notify all players
        state.remove_from_joiner_queue(game_id, username)
        socketio.emit("player_dequeued", {"game_id": game_id, "username": username})
        socketio.emit("message", "You've been admitted to the game! You will be redirected to the game page when the next hand begins.", to=username)

def emit_next_player_turn(game_id: str) -> bool:
    """
    Emits the next player_turn event. 
    returns: True if a player_turn event is emitted, False if the hand ends due to auto-folding
    """
    game = state.get_game(game_id)

    while not game.is_action_finished:
        data = game.get_player_to_act_and_actions() # {"player_to_act": str, "actions": [{"action": , "min": , "allin": }, {...}]}

        # if the player left the game, fold for them
        if data["player_to_act"] in state.get_leaver_queue(game_id):
            print(f"{data['player_to_act']} has left - auto-folding")
            handle_player_action_and_emit_state(game_id, data["player_to_act"], "fold", None)
            continue
        else:
            emit_player_turn(game_id)
            return True
        
    return False

def handle_player_action_and_emit_state(game_id: str, username: str, action: str, amount: int| None):
    game = state.get_game(game_id)
    game.handle_player_action(username, action, amount)
    emit_updated_game_state(game)

def cancel_old_player_timer(game_id: str, username: str):
    timer = state.get_player_timer(game_id, username)
    if timer:
        print(f"canceling timer {timer} for {username}")
        state.cancel_and_remove_player_timer(game_id, username)

def handle_player_action_helper(username: str, game_id: str, action: str, amount: int | None):
    cancel_old_player_timer(game_id, username)
    handle_player_action_and_emit_state(game_id, username, action, amount)
    if emit_next_player_turn(game_id):
        return
    # action must be over
    handle_end_of_round(game_id)

def handle_start_game_helper(game_id: str):
    state.set_game_status(game_id, StatusEnum.in_progress.value)
    poker_players = create_and_fund_players(state.get_players(game_id), state.get_buy_in(game_id))

    game = PokerRound(poker_players, small_blind=state.get_small_blind(game_id), big_blind=state.get_big_blind(game_id))
    print(game)
    game.start_round()
    state.set_game(game_id, game)
    socketio.emit("game_started", {"message": "Game started successfully"}, to=game_id)
    emit_player_turn(game_id)

def kick_broke_players(game_id: str):
    game = state.get_game(game_id)
    small_blind_amount = state.get_small_blind(game_id)
    for username in state.get_players(game_id):
        if game.get_player(username).chips <= small_blind_amount:
            socketio.emit("message", "You don't have enough chips to continue. You won't be joining the next hand unless you re-buy-in.", to=username)
            state.append_to_leaver_queue(game_id, username)
    
def handle_end_of_round(game_id):
    pot_award_info = emit_round_over(game_id)

    # determine which players, if any, must show their hands
    emit_revealed_hands(game_id, pot_award_info)

    # kick brokies
    kick_broke_players(game_id)

    # leavers
    if not cleanup_leavers(game_id):
        return # host left, game deleted
    # joiners
    cleanup_joiners(game_id)

    # set status and await next round
    state.set_game_status(game_id, StatusEnum.between_hands.value)
    emit_countdown(game_id, 10, "round_countdown")
    start_next_round_after_delay(current_app._get_current_object(), game_id)

def emit_countdown(game_id, seconds, event_name):
    def countdown():
        for i in reversed(range(seconds + 1)):
            socketio.emit(event_name, {"seconds": i}, to=game_id)
            time.sleep(1)
    
    Thread(target=countdown).start()

def start_next_round_after_delay(app, game_id, delay=10):
    def start_next_round():
        game = state.get_game(game_id)
        if not game:
            print("Tried to start next round, but the game was already deleted!")
            return

        if game.get_player_count() < 2:
            with app.app_context():
                socketio.emit("error", {"message": "Too few players to continue."})
                delete_game(game_id)
            return
        
        state.set_game_status(game_id, StatusEnum.in_progress.value)
        
        game.start_next_round()
        socketio.emit("game_started", {"message": "Game joined successfully"}, to=game_id)
        
        emit_updated_game_state(game)
        with app.app_context():
            emit_player_turn(game_id)
      
    Timer(delay, start_next_round).start()