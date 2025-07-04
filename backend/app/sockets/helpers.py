from app.globals import games, connected_users
from app.db import db
from app.models.user import User

def cashout_all_players(game_id: str) -> None:
    game = games[game_id]["game"]
    for username in game.get_players():
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
    for username in (games[game_id]["players"] + games[game_id]["queue"]):
        for sid, state in connected_users.items():
            if state.get("username") == username:
                connected_users[sid]["game_id"] = None
                break