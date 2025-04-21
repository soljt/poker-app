from flask import request
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio
from app.globals import connected_users, games

@socketio.on("join_game")
def handle_join(data):
    """Handles when a user joins the game by submitting their username and adding them to active users/game room"""
    username = connected_users[request.sid]["username"] # user must be in this dict due to connecting
    game_id = data.get("game_id")
    
    if game_id not in games:
        emit("error", {"message": "Game not found!"})
        return
    
    if username in games[game_id]["players"]:
        emit("error", {"message": "You are already in this game!"})
        return
    
    if connected_users[request.sid]["game_id"]:
        emit("error", {"message": "You are already in another game!"})
        return
    
    connected_users[request.sid] = {"username": username, "game_id": game_id}
    games[game_id]["players"].append(username)
    join_room(game_id)
    
    emit("player_joined", {"game_id": game_id, "username": username}, to=game_id)  # notify players in the room
    return game_id

@socketio.on("leave_game")
def handle_leave(data):
    """Handles when a user leaves the game by removing them from active users/game room"""
    username = connected_users[request.sid]["username"]
    game_id = data.get("game_id")
    
    if game_id not in games:
        emit("error", {"message": "Game not found!"})
        return
    
    if username not in games[game_id]["players"]:
        emit("error", {"message": "You aren't even in this game...how did you leave it??"})
        return
    
    connected_users[request.sid]["game_id"] = None
    games[game_id]["players"].remove(username)
    emit("message", f"User {username} left the game", to=game_id)
    leave_room(game_id)
    emit("player_left", {"game_id": game_id, "username": username}, broadcast=True)  # notify all others to update Lobby

@socketio.on("create_game")
def handle_create_game(data):
    username = connected_users[request.sid]["username"]
    game_id = f"game_{username}"

    # could be better - check all hosts of all games
    if game_id in games:
        emit("error", {"message": "You have already created a game."})
        return
    
    connected_users[request.sid] = {"username": username, "game_id": game_id} # TODO remove the username overwrite
    games[game_id] = {"host" : username, "players": [username]}
    join_room(game_id)
    emit("game_created", {"game_id": game_id, "host": username, "players": [username for username in games[game_id]["players"]]}, broadcast=True) # all players can see
    return game_id

@socketio.on("delete_game")
def handle_delete_game(data):
    username = connected_users[request.sid]["username"]
    game_id = data.get("game_id")

    if game_id not in games or games[game_id]["host"] != username:
        emit("error", {"message": "You are not the host or game does not exist."})
        return

    # ugly inefficient removal from active_users - consider simply maintaining a mapping from sid to username
    for username in games[game_id]["players"]:
        for sid, state in connected_users.items():
            if state.get("username") == username:
                connected_users[sid]["game_id"] = None
                break

    del games[game_id]
    emit("message", f"Game {game_id} deleted!", to=game_id)
    emit("game_deleted", {"game_id": game_id}, broadcast=True)
    return game_id

@socketio.on("get_games")
def handle_get_games():
    return [{"game_id" : game_id, "host": games[game_id]["host"], "players": [username for username in games[game_id]["players"]]} for game_id in games]