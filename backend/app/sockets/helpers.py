from app.extensions import socketio
from app.db import db
from app.models.user import User
from app.game_logic.game_logic import Player, PokerRound
import app.state as state

class UserValidationError(Exception):
    def __init__(self, reason="Could not find the user in active users"):
        super().__init__(f"{reason}")
        self.reason = reason

def validate_player(request):
    username, game_id = state.get_connected_user(request.sid)
    if not (username and game_id):
        raise UserValidationError
    return username, game_id

def cashout_all_players(game_id: str) -> None:
    game = state.get_game(game_id)
    for username in game.get_players():
        cashout_player(game, username)

def cashout_player(game: PokerRound, username: str) -> None:
    player = game.get_player(username)
    if player:
        stack = player.chips
        print(f"cashing out {username}, with {stack} chips")
        update_player_chips(username, get_user_bankroll(username) + stack)
        player.chips = 0
    else:
        print(f"No player object found for player with username {username}")

def get_user_bankroll(username: str) -> int:
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    return user.chips if user else 0
   
# user db object
def get_user_role(username: str):
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    return user.role if user else ""

def update_player_chips(username, amount):
    if amount < 0:
        raise Exception("Cannot have a negative chip balance!")
    actor = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    actor.chips = amount
    db.session.commit()

def remove_users_from_game(game_id: str) -> None:
    for username in state.get_players(game_id) + state.get_joiner_queue(game_id):
        sid = state.get_user_sid(username)
        state.set_connected_user(None, username, sid)

def cashout_and_remove_player(game_id: str, username: str):
    cashout_player(state.get_game(game_id), username)
    remove_user_from_game(game_id, username)

# called between rounds when a player needs to be removed
def remove_user_from_game(game_id: str, username: str):
    game = state.get_game(game_id)

    player = game.get_player(username)
    game.remove_player(player)
            
    sid = state.get_user_sid(username)
    state.set_connected_user(None, username, sid)

    state.remove_from_leaver_queue(game_id, username)
    state.remove_from_players(game_id, username)
    socketio.emit("player_left", {"game_id": game_id, "username": username})  # notify all others to update Lobby

def delete_game(game_id: str):
    game = state.get_game(game_id)
    if game:
        game.refund_pot()
        cashout_all_players(game_id)
        
    remove_users_from_game(game_id)
    state.remove_game(game_id)
    state.delete_player_timers(game_id)
    socketio.emit("message", f"Game {game_id} deleted!", to=game_id)
    socketio.close_room(game_id)

    socketio.emit("game_deleted", {"game_id": game_id})
    return game_id

def create_and_fund_player(username, buy_in) -> Player:
    update_player_chips(username, get_user_bankroll(username) - buy_in)
    return create_player_object(username, buy_in)

def create_and_fund_players(player_names: list[str], buy_in: int) -> list[Player]:
    poker_players = []
    # create Player objects
    for username in player_names:
        poker_players.append(create_and_fund_player(username, buy_in))
    return poker_players

def create_player_object(username: str, chips: int = -1) -> Player:
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    new_player = Player(username, chips) if chips != -1 else Player(username, user.chips)
    return new_player
                