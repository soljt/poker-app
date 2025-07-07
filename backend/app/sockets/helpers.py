from app.extensions import socketio
from app.globals import games, connected_users
from app.db import db
from app.models.user import User
from app.game_logic.game_logic import Player, PokerRound

class UserValidationError(Exception):
    def __init__(self, reason="Could not find the user in active users"):
        super().__init__(f"{reason}")
        self.reason = reason

def validate_player(request):
    username = connected_users.get(request.sid).get("username")
    game_id = connected_users.get(request.sid).get("game_id")
    if not (username and game_id):
        raise UserValidationError
    return username, game_id

def create_player_object(username: str, chips: int = -1) -> Player:
    try:
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
        new_player = Player(username, chips) if chips != -1 else Player(username, user.chips)
        return new_player
    except Exception as e:
        socketio.emit("error", {"message": str(e)}, to=username)
        return

def cashout_all_players(game_id: str) -> None:
    game = games[game_id]["game"]
    for username in game.get_players():
        cashout_player(game, username)

def cashout_player(game: PokerRound, username: str) -> None:
    player = game.get_player(username)
    stack = player.chips
    print(f"cashing out {username}, with {stack} chips")
    update_player_chips(username, get_user_bankroll(username) + stack)

def get_user_bankroll(username: str) -> int:
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    return user.chips if user else 0
   
def update_player_chips(username, amount):
    actor = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    actor.chips = amount
    db.session.commit()

def remove_users_from_game(game_id: str) -> None:
    # ugly inefficient removal from active_users - consider simply maintaining a mapping from sid to username
    for username in (games[game_id]["players"] + games[game_id]["joiner_queue"]):
        for sid, state in connected_users.items():
            if state.get("username") == username:
                connected_users[sid]["game_id"] = None
                break

# called between rounds when a player needs to be removed
def remove_user_from_game(game_id: str, username: str):
    game = games[game_id]["game"]

    player = game.get_player(username)
    game.remove_player(player)
            
    for sid, state in connected_users.items():
        if state.get("username") == username:
            connected_users[sid]["game_id"] = None
            break

    games[game_id]["players"].remove(username)

    games[game_id]["leaver_queue"].remove(username)
    socketio.emit("player_left", {"game_id": game_id, "username": username})  # notify all others to update Lobby

                