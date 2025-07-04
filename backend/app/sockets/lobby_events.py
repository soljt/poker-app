from flask import request
from flask_socketio import close_room, emit, join_room, leave_room
from app.extensions import socketio
from app.globals import connected_users, games, StatusEnum
from app.sockets.helpers import cashout_all_players, get_user_bankroll, remove_users_from_game

def get_game_info(game_id: str):
    return {"game_id" : game_id, 
             "host": games[game_id]["host"], 
             "players": games[game_id]["players"], 
             "small_blind": games[game_id]["small_blind"],
             "big_blind": games[game_id]["big_blind"],
             "buy_in": games[game_id]["buy_in"],
             "table_max": games[game_id]["table_max"],
             "status": games[game_id]["status"], 
             "queue": games[game_id]["queue"]}

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
    
    if get_user_bankroll(username) < games[game_id]["buy_in"]:
        emit("error", {"message": "You don't have enough to buy in to this game..."})
        return
    
    connected_users[request.sid] = {"username": username, "game_id": game_id}
    if games[game_id].get("status", "") == "waiting_to_start":
        games[game_id]["players"].append(username)
        emit("player_joined", {"game_id": game_id, "username": username}, broadcast=True)  # notify all players
    else:
        games[game_id]["queue"].append(username)
        emit("player_queued", {"game_id": game_id, "username": username}, broadcast=True)
    join_room(game_id)
    
    return game_id

@socketio.on("leave_game")
def handle_leave(data):
    """Handles when a user leaves the game by removing them from active users/game room"""
    username = connected_users[request.sid]["username"]
    game_id = data.get("game_id")
    
    if game_id not in games:
        emit("error", {"message": "Game not found!"})
        return
    
    if username not in (games[game_id]["players"] + games[game_id]["queue"]):
        emit("error", {"message": "You aren't even in this game...how did you leave it??"})
        return
    
    connected_users[request.sid]["game_id"] = None
    if username in games[game_id]["players"]:
        games[game_id]["players"].remove(username)
        emit("player_left", {"game_id": game_id, "username": username}, broadcast=True)  # notify all others to update Lobby
    else:
        games[game_id]["queue"].remove(username)
        emit("player_dequeued", {"game_id": game_id, "username": username}, broadcast=True)  # notify all others to update Lobby
    leave_room(game_id)
    

@socketio.on("create_game")
def handle_create_game(data):
    username = connected_users[request.sid]["username"]
    game_id = f"game_{username}"

    # could be better - check all hosts of all games
    if game_id in games:
        emit("error", {"message": "You have already created a game."})
        return
    
    if get_user_bankroll(username) < data["buy_in"]:
        emit("error", {"message": "You don't have enough to buy in to your own game..."})
        return
    
    connected_users[request.sid] = {"username": username, "game_id": game_id} # TODO remove the username overwrite
    games[game_id] = {
        "host" : username, 
        "players": [username], 
        "small_blind": data["small_blind"],
        "big_blind": data["big_blind"],
        "buy_in": data["buy_in"],
        "table_max": data["table_max"],
        "status": StatusEnum.waiting_to_start.value, 
        "queue": []}
    join_room(game_id)
    emit("game_created", get_game_info(game_id), broadcast=True) # all players can see
    return game_id

@socketio.on("delete_game")
def handle_delete_game(data):
    username = connected_users[request.sid]["username"]
    game_id = data.get("game_id")

    if game_id not in games or games[game_id]["host"] != username:
        emit("error", {"message": "You are not the host or game does not exist."})
        return

    if games[game_id].get("game"):
        cashout_all_players(game_id)

    remove_users_from_game(game_id)
    del games[game_id]
    emit("message", f"Game {game_id} deleted!", to=game_id)
    close_room(game_id)

    emit("game_deleted", {"game_id": game_id}, broadcast=True)
    return game_id

@socketio.on("get_games")
def handle_get_games():
    return [get_game_info(game_id) for game_id in games]