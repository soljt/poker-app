import enum
games = {} 
# games[game_id] = {
#     "players" : [], 
#     "host": str, 
#     "game": PokerRound, 
#     "small_blind": int,
#     "big_blind": int,
#     "buy_in": int,
#     "status": StatusEnum, 
#     "joiner_queue": [],
#     "leaver_queue": []} - "game" is not set until game is started by host

connected_users = {} # active_users[socket_sid] = {"username": str, "game_id": str} - user doesn't become "active" unless they get a game_id, otherwise null
player_timers = {} # {game_id: {username: InactionTimer}}
user_sids = {} # user_sids[username] = sid

class StatusEnum(enum.Enum):
    waiting_to_start = "waiting_to_start"
    between_hands = "between_hands"
    in_progress = "in_progress"