from flask import request
from flask_socketio import close_room, emit, join_room, leave_room
from app.extensions import socketio
from app.globals import connected_users, games, StatusEnum
from app.sockets.helpers import cashout_all_players, cashout_player, get_user_bankroll, remove_user_from_game, remove_users_from_game, update_player_chips
from app.sockets.game_events import create_player_object

def get_game_info(game_id: str):
    return {"game_id" : game_id, 
             "host": games[game_id]["host"], 
             "players": games[game_id]["players"], 
             "small_blind": games[game_id]["small_blind"],
             "big_blind": games[game_id]["big_blind"],
             "buy_in": games[game_id]["buy_in"],
             "table_max": games[game_id]["table_max"],
             "status": games[game_id]["status"], 
             "joiner_queue": games[game_id]["joiner_queue"]}

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
    if games[game_id].get("status", "") == StatusEnum.waiting_to_start.value:
        games[game_id]["players"].append(username)
        emit("player_joined", {"game_id": game_id, "username": username}, broadcast=True)  # notify all players

    elif games[game_id].get("status", "") == StatusEnum.between_hands.value:
        # TODO ensure table does not exceed seat limit
        update_player_chips(username, get_user_bankroll(username) - games[game_id]["buy_in"])
        games[game_id]["game"].add_player(create_player_object(username, games[game_id]["buy_in"]))
        games[game_id]["players"].append(username)
        emit("player_joined", {"game_id": game_id, "username": username}, broadcast=True)  # notify all players
        
    else:
        games[game_id]["joiner_queue"].append(username)
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
    
    if username not in (games[game_id]["players"] + games[game_id]["joiner_queue"]):
        emit("error", {"message": "You aren't even in this game...how did you leave it??"})
        return
    
    leave_room(game_id)

    # case where game has not yet begun or the leaver is only queued up
    if not games[game_id].get("game") or username not in games[game_id]["players"]:
        connected_users[request.sid]["game_id"] = None
        if username in games[game_id]["players"]:
            games[game_id]["players"].remove(username)
            emit("player_left", {"game_id": game_id, "username": username}, broadcast=True)  # notify all others to update Lobby
        else:
            games[game_id]["joiner_queue"].remove(username)
            emit("player_dequeued", {"game_id": game_id, "username": username}, broadcast=True)  # notify all others to update Lobby
        return
    
    # case where game is ongoing and player is a participant
    games[game_id]["leaver_queue"].append(username)

    # case where game is between hands - can remove at will
    if games[game_id]["status"] == StatusEnum.between_hands.value:
        cashout_player(games[game_id]["game"], username)
        remove_user_from_game(game_id, username)

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
        "joiner_queue": [],
        "leaver_queue": []}
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
        games[game_id]["game"].refund_pot()
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