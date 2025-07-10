import app.state as state
from flask_socketio import emit
from app.sockets.helpers import cashout_and_remove_player, get_user_bankroll, create_and_fund_player
from app.globals import StatusEnum

def validate_join_game(game_id: str, connected_game_id: str | None, username: str) -> bool:
    if not state.check_game_id(game_id):
        emit("error", {"message": "Game not found!"})
        return False 
    if username in state.get_players(game_id):
        emit("error", {"message": "You are already in this game!"})
        return False 
    if connected_game_id:
        emit("error", {"message": "You are already in another game!"})
        return False
    if get_user_bankroll(username) < state.get_buy_in(game_id):
        emit("error", {"message": "You don't have enough to buy in to this game..."})
        return False
    return True
    
def join_game(game_id: str, username: str):

    state.set_connected_user(game_id, username, state.get_user_sid(username))

    status = state.get_game_status(game_id)
    game = state.get_game(game_id)
    if status == StatusEnum.in_progress.value or game and game.get_player_count() + 1 > game.get_max_seats() or len(state.get_players(game_id)) == 8:
        state.append_to_joiner_queue(game_id, username)
        emit("player_queued", {"game_id": game_id, "username": username}, broadcast=True)

    elif status == StatusEnum.waiting_to_start.value:
        state.append_to_players(game_id, username)
        emit("player_joined", {"game_id": game_id, "username": username}, broadcast=True)  # notify all players

    elif status == StatusEnum.between_hands.value:
        # TODO ensure table does not exceed seat limit
        add_new_player(game_id, username)

def add_new_player(game_id: str, username: str):
    state.get_game(game_id).add_player(create_and_fund_player(username, state.get_buy_in(game_id)))
    state.append_to_players(game_id, username)
    emit("player_joined", {"game_id": game_id, "username": username}, broadcast=True)  # notify all players

def validate_reconnect_to_game(game_id: str, connected_game_id: str, username: str) -> bool:
    if not state.check_game_id(game_id):
        emit("error", {"message": "Game not found!"})
        return False
    if connected_game_id and connected_game_id != game_id:
        emit("error", {"message": "You are already in another game!"})
        return False
    if not username in state.get_players(game_id):
        emit("error", "You're not in this game and therefore cannot reconnect.")
        return False
    return True

def reconnect_to_game(game_id: str, username: str):
    if username in state.get_leaver_queue(game_id):
        state.remove_from_leaver_queue(game_id, username)
    sid = state.get_user_sid(username)
    state.set_connected_user(game_id, username, sid)
    emit("message", f"User {username} reconnected!", to=game_id) 

def validate_leave_game(game_id: str, username: str):
    if not state.check_game_id(game_id):
        emit("error", {"message": "Game not found!"})
        return
    
    player_list = state.get_players(game_id)
    if username not in (player_list + state.get_joiner_queue(game_id)):
        emit("error", {"message": "You aren't even in this game...how did you leave it??"})
        return
    
def leave_game(game_id: str, username: str):
    game = state.get_game(game_id)
    player_list = state.get_players(game_id)
    # case where game has not yet begun or the leaver is only queued up
    if not game or username not in player_list:
        state.set_connected_user(None, username, state.get_user_sid(username))
        if username in player_list:
            state.remove_from_players(game_id, username)
            emit("player_left", {"game_id": game_id, "username": username}, broadcast=True)  # notify all others to update Lobby
        else:
            state.remove_from_joiner_queue(game_id, username)
            emit("player_dequeued", {"game_id": game_id, "username": username}, broadcast=True)  # notify all others to update Lobby
        return
    
    # case where game is ongoing and player is a participant
    state.append_to_leaver_queue(game_id, username)

    # case where game is between hands - can remove at will
    if state.get_game_status(game_id) == StatusEnum.between_hands.value:
        cashout_and_remove_player(game_id, username) # also removes from leaver queue
    
    emit("error", {"message": f"User {username} left the game!"}, to=game_id)

def validate_create_game(game_id: str, username: str, buy_in: int):
    # could be better - check all hosts of all games
    if state.check_game_id(game_id):
        emit("error", {"message": "You have already created a game."})
        return game_id
    
    if get_user_bankroll(username) < buy_in:
        emit("error", {"message": "You don't have enough to buy in to your own game..."})
        return ""
    
    return True

def get_game_info(game_id: str):
    return {"game_id" : game_id, 
             "host": state.get_host(game_id), 
             "players": state.get_players(game_id), 
             "small_blind": state.get_small_blind(game_id),
             "big_blind": state.get_big_blind(game_id),
             "buy_in": state.get_buy_in(game_id),
             "status": state.get_game_status(game_id), 
             "joiner_queue": state.get_joiner_queue(game_id)}

def create_game(game_id: str, username: str, small_blind: int, big_blind: int, buy_in: int):
    state.set_connected_user(game_id, username, state.get_user_sid(username)) # TODO remove the username overwrite 
    state.set_new_game_id(
        game_id=game_id, 
        username=username,
        small_blind=small_blind,
        big_blind=big_blind,
        buy_in=buy_in
        )
    emit("game_created", get_game_info(game_id), broadcast=True) # all players can see