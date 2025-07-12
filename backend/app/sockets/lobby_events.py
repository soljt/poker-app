from flask import request
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio
from app.sockets.helpers import delete_game, get_user_role
import app.state as state
from app.sockets.lobby_flow import create_game, get_game_info, join_game, leave_game, reconnect_to_game, validate_create_game, validate_join_game, validate_leave_game, validate_reconnect_to_game
from app.models.user import RoleEnum

@socketio.on("join_game")
def handle_join(data):
    """Handles when a user joins the game by submitting their username and adding them to active users/game room"""
    username, connected_game_id = state.get_connected_user(request.sid) # user must be in this dict due to connecting
    game_id = data.get("game_id")
    
    if not validate_join_game(game_id, connected_game_id, username):
        return
    
    join_game(game_id, username)
    join_room(game_id)
    
    return game_id

@socketio.on("reconnect_to_game")
def handle_reconnect_to_game(data) -> bool: # returns True if the frontend should let you back in
    username, connected_game_id = state.get_connected_user(request.sid) # user must be in this dict due to connecting
    game_id = data.get("game_id")

    if not validate_reconnect_to_game(game_id, connected_game_id, username):
        return False
    
    join_room(game_id)
    reconnect_to_game(game_id, username)     
    
    return True

@socketio.on("leave_room")
def handle_leave_room(data):
    leave_room(data.get("game_id"))

@socketio.on("leave_game")
def handle_leave(data):
    """Handles when a user leaves the game by removing them from active users/game room"""
    username, _ = state.get_connected_user(request.sid)
    game_id = data.get("game_id")
    
    validate_leave_game(game_id, username)
    
    leave_room(game_id)

    leave_game(game_id, username)

@socketio.on("create_game")
def handle_create_game(data):
    username, _ = state.get_connected_user(request.sid)
    game_id = f"game_{username}"

    val = validate_create_game(game_id, username, data["buy_in"])
    if val != True:
        return val
    
    create_game(game_id, username, data["small_blind"], data["big_blind"], data["buy_in"])
    join_room(game_id)
    return game_id

@socketio.on("delete_game")
def handle_delete_game(data):
    username, _ = state.get_connected_user(request.sid)
    game_id = data.get("game_id")

    if not state.check_game_id(game_id) or (state.get_host(game_id) != username and get_user_role(username) != RoleEnum.admin):
        emit("error", {"message": f"You are not the host or game does not exist. Host is: {state.get_host(game_id)}."})
        return

    return delete_game(game_id)

@socketio.on("get_games")
def handle_get_games():
    return [get_game_info(game_id) for game_id in state.get_game_ids()]