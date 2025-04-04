from app.home import home
from app.db import db
from app.models.user import User
from app import games, connected_users, session

# DEBUG ONLY: print db contents
@home.route("/")
def hello_world():
    users = db.session.execute(db.select(User)).scalars().all()
    users_string = ("\n").join([f"<h1>{user.to_dict()}</h1>" for user in users])
    return f"<h1>users: \n{users_string}</h1>\n<h2>session: {session}</h2>"

# DEBUG ONLY: print current games
@home.route("/print_games")
def print_games():
    lines = []
    lines.append(f"<h4>game_ids: {[{game_id} for game_id in games]}</h4>")
    lines.append(f"<h4>connected users: {[f"SID: {sid}, dict: {user_game}\n" for sid, user_game in connected_users.items()]}</h4>")
    return "\n".join(lines)