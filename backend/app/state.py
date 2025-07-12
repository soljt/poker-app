from app.globals import StatusEnum, games
from app.globals import player_timers, connected_users, user_sids
from app.game_logic.game_logic import PokerRound
from app.timer.inaction_timer import InactionTimer

def check_game_id(game_id: str) -> bool:
    return game_id in games

def get_game_ids() -> list[str]:
    return [game_id for game_id in games]

def set_new_game_id(game_id: str, username:str, small_blind: int, big_blind: int, buy_in: int):
    games[game_id] = {
        "host" : username, 
        "players": [username], 
        "small_blind": small_blind,
        "big_blind": big_blind,
        "buy_in": buy_in,
        "status": StatusEnum.waiting_to_start.value, 
        "joiner_queue": [],
        "leaver_queue": []}

def get_game(game_id: str) -> PokerRound | None:
    return games.get(game_id, {}).get("game")

def set_game(game_id: str, game: PokerRound):
    games[game_id]["game"] = game

def remove_game(game_id: str):
    if games.get(game_id):
        del games[game_id]

def get_host(game_id:str) -> str:
    return games.get(game_id, {}).get("host")

def set_host(game_id:str, username: str):
    games.get(game_id, {})["host"] = username

def get_buy_in(game_id:str) -> int:
    return games.get(game_id, {}).get("buy_in")

def get_small_blind(game_id:str) -> int:
    return games.get(game_id, {}).get("small_blind")

def get_big_blind(game_id:str) -> int:
    return games.get(game_id, {}).get("big_blind")

# leaver queue
def get_leaver_queue(game_id: str) -> list[str]:
    return games.get(game_id, {}).get("leaver_queue")

def append_to_leaver_queue(game_id: str, username: str):
    if not games.get(game_id, {}).get("leaver_queue"):
        games[game_id]["leaver_queue"] = [username]
    else:
        games[game_id]["leaver_queue"].append(username)

def remove_from_leaver_queue(game_id: str, username: str):
    arr = games.get(game_id, {}).get("leaver_queue", [])
    if username in arr:
        arr.remove(username)

# joiner queue
def get_joiner_queue(game_id: str) -> list[str]:
    return games.get(game_id, {}).get("joiner_queue")

def append_to_joiner_queue(game_id: str, username: str):
    if not games.get(game_id, {}).get("joiner_queue"):
        games[game_id]["joiner_queue"] = [username]
    else:
        games[game_id]["joiner_queue"].append(username)

def remove_from_joiner_queue(game_id: str, username: str):
    arr = games.get(game_id, {}).get("joiner_queue", [])
    if username in arr:
        arr.remove(username)

# players 
def get_players(game_id: str) -> list[str]:
    return games.get(game_id, {}).get("players")

def append_to_players(game_id: str, username: str):
    games.get(game_id, {}).get("players").append(username)

def remove_from_players(game_id: str, username: str):
    arr = games.get(game_id, {}).get("players", [])
    if username in arr:
        arr.remove(username)

# status
def get_game_status(game_id: str) -> StatusEnum:
    return games.get(game_id, {}).get("status", "")

def set_game_status(game_id: str, status: StatusEnum):
    games[game_id]["status"] = status

# player timers
def get_player_timer(game_id: str, username: str) -> InactionTimer | None:
    return player_timers.get(game_id, {}).get(username)

def set_player_timer(game_id: str, username: str, timer: InactionTimer):
    if not player_timers.get(game_id):
        player_timers[game_id] = {username: timer}
    else:
        player_timers[game_id][username] = timer

def cancel_and_remove_player_timer(game_id: str, username: str):
    timer = player_timers.get(game_id).pop((username), None)
    if timer:
        timer.cancel()

def delete_player_timers(game_id: str):
    timers = player_timers.pop(game_id, {})
    for timer in timers.values():
        timer.cancel()
        timer.cleanup()

# connected_users
def get_connected_user(sid: str) -> tuple[str, str]:
    entry = connected_users.get(sid, {})
    return entry.get("username"), entry.get("game_id")

def set_connected_user(game_id: str | None, username: str, sid: str):
    connected_users[sid] = {"username": username, "game_id": game_id}

def delete_connected_user(sid: str):
    if connected_users.get(sid):
        del connected_users[sid]

# user_sids
def get_user_sid(username: str) -> str:
    return user_sids.get(username, "")

def set_user_sid(username: str, sid: str):
    user_sids[username] = sid