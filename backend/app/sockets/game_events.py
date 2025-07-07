from flask import current_app, request, copy_current_request_context
from flask_socketio import emit
from app.extensions import socketio
from app.globals import StatusEnum, connected_users, games
from app.db import db
from app.models.user import User
from app.game_logic.game_logic import PokerRound, Player
from threading import Timer
from app.sockets.helpers import cashout_all_players, cashout_player, remove_users_from_game, update_player_chips, get_user_bankroll, remove_user_from_game, validate_player, create_player_object
# from run import app

@socketio.on("start_game")
def handle_start_game(data):
    """Host starts the game, and hands are dealt."""
    username = connected_users[request.sid]["username"]
    game_id = data.get("game_id")
    if game_id not in games or games[game_id]["host"] != username:
        emit("error", {"message": "You are not the host or game does not exist."})
        return

    player_names = games[game_id]["players"]

    if len(player_names) < 2:
        emit("error", {"message": "At least 2 players needed to start!"})
        return
    
    games[game_id]["status"] = StatusEnum.in_progress.value
    poker_players = []
    # create Player objects
    for username in player_names:
        try:
            update_player_chips(username, get_user_bankroll(username) - games[game_id]["buy_in"])
            poker_players.append(create_player_object(username, games[game_id]["buy_in"]))
        except Exception as e:
            emit("error", {"message": str(e)})
            return

    game = PokerRound(poker_players, small_blind=games[game_id]["small_blind"], big_blind=games[game_id]["big_blind"])
    game.start_round()
    games[game_id]["game"] = game
    emit("game_started", {"message": "Game started successfully"}, to=game_id)
    data = game.get_player_to_act_and_actions() # {"player_to_act": Player, "actions": [{"action": , "min": , "allin": }, {}]}
    emit("player_turn", data, to=game_id)

@socketio.on("player_action")
def handle_player_action(data):
    try:
        username, game_id = validate_player(request)
        game = games[game_id]["game"]
        print(f"data received on player {username} action:", data)
        game.handle_player_action(username, data.get("action"), data.get("amount"))
        print("done handling action")

        for name in game.get_players():
            print(f"doing shit for {name}")
            game_state = game.serialize_for_player(name)
            print(f"emitting game state to {name}")
            emit("update_game_state", game_state, to=name)
        
        while not game.is_action_finished:
            print("action not finished")
            data = game.get_player_to_act_and_actions() # {"player_to_act": str, "actions": [{"action": , "min": , "allin": }, {...}]}

            # if the player left the game, fold for them
            if data["player_to_act"] in games[game_id]["leaver_queue"]:
                print(f"{data["player_to_act"]} has left - auto-folding")
                game.handle_player_action(data["player_to_act"], "fold", None)
                continue
            else:
                emit("player_turn", data, to=game_id)
                return
            
        # implied "else:"
        print("action IS FINISHED")
        pot_award_info = game.end_poker_round() # [{"winners": list[str], "amount": int, "share": int}, {...}]
        for name in game.get_players(): # additional update to show newly dealt cards if needed
            game_state = game.serialize_for_player(name)
            print(f"emitting game state to {name}")
            emit("update_game_state", game_state, to=name)

        print("emitting round over")

        emit("round_over", pot_award_info, to=game_id)
        # TODO check whether there are enough players to start the next hand (considering leavers and joiners)
        # leavers
        for username in games[game_id]["leaver_queue"]:
            cashout_player(game, username)
            remove_user_from_game(game_id, username)
        # joiners
        for username in games[game_id]["joiner_queue"]:
            # TODO ensure table does not exceed seat limit
            update_player_chips(username, get_user_bankroll(username) - games[game_id]["buy_in"])
            game.add_player(create_player_object(username, games[game_id]["buy_in"]))
            games[game_id]["players"].append(username)
            emit("player_joined", {"game_id": game_id, "username": username}, broadcast=True)  # notify all players
            games[game_id]["joiner_queue"].remove(username)
            emit("player_dequeued", {"game_id": game_id, "username": username}, broadcast=True)
        games[game_id]["status"] = StatusEnum.between_hands.value
        emit_countdown(game_id, 10)
        start_next_round_after_delay(game_id)
    except Exception as e:
        emit("error", {"message": str(e)})
        # TODO remove this lol
        raise e
        return
    
def emit_countdown(game_id, seconds_left):
    socketio.emit("round_countdown", {"seconds": seconds_left}, to=game_id)
    if seconds_left > 0:
        Timer(1, emit_countdown, args=(game_id, seconds_left - 1)).start()

def start_next_round_after_delay(game_id, delay=10):
    @copy_current_request_context
    def start_round():
        if not games.get(game_id):
            print("Tried to start next round, but the game was already deleted!")
            return
        
        # TODO check whether there are enough players to start the next hand (considering leavers and joiners)
        if games[game_id]["game"].get_player_count() < 2:
            cashout_all_players(game_id)
                
            remove_users_from_game(game_id)
            del games[game_id]
            emit("message", f"Game {game_id} deleted due to lack of players!", to=game_id)
            socketio.close_room(game_id)
            emit("game_deleted", {"game_id": game_id}, broadcast=True)
            return
        
        games[game_id]["status"] = StatusEnum.in_progress.value
        game = games[game_id]["game"]
        game.start_next_round()
        socketio.emit("game_started", {"message": "Game joined successfully"}, to=game_id)
        for name in game.get_players():
            game_state = game.serialize_for_player(name)
            print(f"emitting game state to {name}")
            socketio.emit("update_game_state", game_state, to=name)
        data = game.get_player_to_act_and_actions() # {"player_to_act": Player, "actions": [{"action": , "min": , "allin": }, {}]}
        socketio.emit("player_turn", data, to=game_id)
      
    Timer(delay, start_round).start()

@socketio.on("get_hand")
def handle_get_hand():
    username, game_id = validate_player(request)

    game = games[game_id]["game"]
    hand = game.get_player_hand(username)
    return hand