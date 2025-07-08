from flask import current_app, request
from flask_socketio import emit
from app.extensions import socketio
from app.globals import StatusEnum, connected_users, games
from app.game_logic.game_logic import PokerRound
from threading import Timer
from app.sockets.helpers import cashout_all_players, cashout_player, remove_users_from_game, update_player_chips, get_user_bankroll, remove_user_from_game, validate_player, create_player_object
from app.sockets.helpers import delete_game
# from run import app

player_timers = {} # {(game_id, username): (kick_thread, count_thread)}

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
    kick_player_after_delay(current_app._get_current_object(), game_id, data["player_to_act"], 5) # KICK THE INACTIVE PLAYER

@socketio.on("player_action")
def handle_player_action(data):
    try:
        username, game_id = validate_player(request)
        
        key = (game_id, username)
        if (game_id, username) in player_timers:
            print(f"canceling timer {player_timers[key]} for {username}")
            player_timers[key].cancel()
            del player_timers[key]
            
        handle_player_action_helper(username, game_id, data.get("action"), data.get("amount"))
        print(f"data received on player {username} action:", data)

    except Exception as e:
        emit("error", {"message": str(e)})
        return
    
def handle_player_action_helper(username: str, game_id: str, action: str, amount: int | None):
    game = games[game_id]["game"]
    game.handle_player_action(username, action, amount)

    for name in game.get_players():
        game_state = game.serialize_for_player(name)
        socketio.emit("update_game_state", game_state, to=name)
    
    while not game.is_action_finished:
        data = game.get_player_to_act_and_actions() # {"player_to_act": str, "actions": [{"action": , "min": , "allin": }, {...}]}

        # if the player left the game, fold for them
        if data["player_to_act"] in games[game_id]["leaver_queue"]:
            print(f"{data["player_to_act"]} has left - auto-folding")
            game.handle_player_action(data["player_to_act"], "fold", None)
            for name in game.get_players():
                game_state = game.serialize_for_player(name)
                socketio.emit("update_game_state", game_state, to=name)
            continue
        else:
            socketio.emit("player_turn", data, to=game_id)
            kick_player_after_delay(current_app._get_current_object(), game_id, data["player_to_act"], 5) # KICK THE INACTIVE PLAYER
            return
        
    # implied "else:"
    pot_award_info = game.end_poker_round() # [{"winners": list[str], "amount": int, "share": int}, {...}]
    for name in game.get_players(): # additional update to show newly dealt cards if needed
        game_state = game.serialize_for_player(name)
        print(f"emitting game state to {name}")
        socketio.emit("update_game_state", game_state, to=name)

    print("emitting round over")

    socketio.emit("round_over", pot_award_info, to=game_id)
    # determine which players, if any, must show their hands
    must_show_players = game.determine_must_show_players(pot_award_info)
    for entry in must_show_players:
        socketio.emit("hand_revealed", entry, to=game_id)

    # leavers
    if games[game_id]["host"] in games[game_id]["leaver_queue"]:
        delete_game(game_id)
        return

    for username in games[game_id]["leaver_queue"][:]:
        print(f"removing {username} from {game_id}")
        cashout_player(game, username)
        remove_user_from_game(game_id, username)
    # joiners
    for username in games[game_id]["joiner_queue"][:]:
        # TODO ensure table does not exceed seat limit
        update_player_chips(username, get_user_bankroll(username) - games[game_id]["buy_in"])
        game.add_player(create_player_object(username, games[game_id]["buy_in"]))
        games[game_id]["players"].append(username)
        socketio.emit("player_joined", {"game_id": game_id, "username": username})  # notify all players
        games[game_id]["joiner_queue"].remove(username)
        socketio.emit("player_dequeued", {"game_id": game_id, "username": username})
    games[game_id]["status"] = StatusEnum.between_hands.value
    emit_countdown(game_id, 10, "round_countdown")
    start_next_round_after_delay(current_app._get_current_object(), game_id)

def emit_countdown(game_id, seconds_left, event_name):
    socketio.emit(event_name, {"seconds": seconds_left}, to=game_id)
    if seconds_left > 0:
        Timer(1, emit_countdown, args=(game_id, seconds_left - 1, event_name)).start()

def kick_player_after_delay(app, game_id: str, username: str, delay: int=30):
    print("called the timer for the kicking")
    timer = PlayerTimer(socketio, app, game_id, username, delay)# Timer(delay, kick_player, [game_id, username])
    player_timers[(game_id, username)] = timer
    
    timer.start()


def start_next_round_after_delay(app, game_id, delay=10):
    def start_round():
        if not games.get(game_id):
            print("Tried to start next round, but the game was already deleted!")
            return
        
        # TODO check whether there are enough players to start the next hand (considering leavers and joiners)
        if games[game_id]["game"].get_player_count() < 2:
            with app.app_context():
                cashout_all_players(game_id)
                
            remove_users_from_game(game_id)
            del games[game_id]
            socketio.emit("message", f"Game {game_id} deleted due to lack of players!", to=game_id)
            socketio.close_room(game_id)
            socketio.emit("game_deleted", {"game_id": game_id})
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
        kick_player_after_delay(app, game_id, data["player_to_act"], 5) # KICK THE INACTIVE PLAYER
      
    Timer(delay, start_round).start()

import threading
import time

class PlayerTimer:
    def __init__(self, socketio, app, game_id, username, delay=30):
        self.socketio = socketio
        self.app = app
        self.game_id = game_id
        self.username = username
        self.delay = delay

        self.kick_timer = None
        self.countdown_thread = None
        self.cancel_event = threading.Event()

    def start(self):
        self.cancel_event.clear()

        # Start countdown
        self.countdown_thread = threading.Thread(target=self._emit_countdown)
        self.countdown_thread.start()

        # Schedule kick
        self.kick_timer = threading.Timer(self.delay, self._kick_player)
        self.kick_timer.start()

    def cancel(self):
        self.cancel_event.set()
        if self.kick_timer:
            self.kick_timer.cancel()

    def _emit_countdown(self):
        seconds_left = self.delay
        while seconds_left >= 0 and not self.cancel_event.is_set():
            self.socketio.emit("kick_countdown", {"seconds": seconds_left}, to=self.username)
            time.sleep(1)
            seconds_left -= 1

    def _kick_player(self):
        if self.cancel_event.is_set():
            return
        with self.app.app_context():
            game = games.get(self.game_id, {}).get("game")
            if not game or str(game.current_player) != self.username:
                return
            print(f"[KICK] Kicking {self.username} from {self.game_id}")
            games[self.game_id]["leaver_queue"].append(self.username)
            print(f"emitting player_kicked to {self.username}")
            socketio.emit("player_kicked", to=self.username)
            handle_player_action_helper(self.username, self.game_id, "fold", None)

@socketio.on("get_hand")
def handle_get_hand():
    username, game_id = validate_player(request)

    game = games[game_id]["game"]
    hand = game.get_player_hand(username)
    return hand

@socketio.on("reveal_hand")
def handle_reveal_hand():
    username, game_id = validate_player(request)

    game = games[game_id]["game"]
    hand = game.get_player_hand(username)
    emit("hand_revealed", {"username": username, "hand": hand}, to=game_id)