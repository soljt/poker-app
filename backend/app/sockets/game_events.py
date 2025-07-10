from flask import request
from flask_socketio import emit
from app.extensions import socketio
import app.state as state
from app.sockets.helpers import validate_player
from app.sockets.game_flow import handle_player_action_helper, handle_start_game_helper

@socketio.on("start_game")
def handle_start_game(data):
    """Host starts the game, and hands are dealt."""
    username, _ = validate_player(request)
    game_id = data.get("game_id")
    if not state.check_game_id(game_id) or state.get_host(game_id) != username:
        emit("error", {"message": "You are not the host or game does not exist."})
        return

    player_names = state.get_players(game_id)
    if len(player_names) < 2:
        emit("error", {"message": "At least 2 players needed to start!"})
        return
    
    handle_start_game_helper(game_id)

@socketio.on("player_action")
def handle_player_action(data):
    try:
        username, game_id = validate_player(request)            
        print(f"data received on player {username} action:", data)
        handle_player_action_helper(username, game_id, data.get("action"), data.get("amount"))
        
    except Exception as e:
        emit("error", {"message": str(e)})
        return

@socketio.on("get_hand")
def handle_get_hand():
    username, game_id = validate_player(request)

    game = state.get_game(game_id)
    hand = game.get_player_hand(username)
    return hand

@socketio.on("reveal_hand")
def handle_reveal_hand():
    username, game_id = validate_player(request)

    game = state.get_game(game_id)
    hand = game.get_player_hand(username)
    emit("hand_revealed", {"username": username, "hand": hand}, to=game_id)