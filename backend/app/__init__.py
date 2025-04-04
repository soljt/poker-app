from datetime import datetime, timedelta, timezone
from flask import Flask, request, session, jsonify
from flask_cors import CORS
from .extensions import jwt, socketio
from flask_jwt_extended import create_access_token, current_user, decode_token, get_csrf_token, get_jwt, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.game.game import PokerRound, Player
from app.db import init_db, db
from app.models.user import User
from sqlalchemy.exc import IntegrityError
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # initialize extensions
    # CORS
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})
    # db - see db.py
    init_db(app)
    # jwt (auth)
    jwt.init_app(app)
    # sockets (game state)
    socketio.init_app(app)

    # import and register jwt handlers
    from app.auth import jwt_handlers
    app.after_request(jwt_handlers.refresh_expiring_jwts)

    # register blueprints
    from app.home import home as home_bp
    from app.auth import auth as auth_bp
    from app.util import util as util_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(util_bp)

    return app

games = {} # games[game_id] = {"players" : [], "host": str, "game": PokerRound} - "game" is not set until game is started by host
connected_users = {} # active_users[socket_sid] = {"username": str, "game_id": str} - user doesn't become "active" unless they get a game_id, otherwise null

@socketio.on("connect")
def connect_handler(auth):
    print(f"New connection attempt with SID: {request.sid}")
    if not request.cookies:
        print("no cookies!")
        return False
    try: 
        decoded = decode_token(request.cookies["access_token_cookie"], request.cookies["csrf_access_token"])   
        user_id = decoded["sub"]
        username = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none().username   
        print(f"connected successfully with {request.sid}")

        # check to see if user is reconnecting under different sid
        for key, dic in connected_users.items():
            if dic.get("username") == username:
                # get the user's joined game and rejoin it
                game_id = dic.get("game_id")
                if game_id:
                    join_room(game_id)
                    emit("message", f"User {username} reconnected!", to=game_id)

                # delete old entry
                del connected_users[key]
                connected_users[request.sid] = dic              
                return
        
        # if this is the first connection, add user to connected_users
        connected_users[request.sid] = {"username": username, "game_id": None}
    except:
        print("failed")
        return False


@socketio.on("disconnect")
def disconnect_handler(reason):
    print(f"closing connection with SID: {request.sid} due to {reason}")
    try:
        username = connected_users.get(request.sid).get("username")
        room = connected_users.get(request.sid).get("game_id")

        # if the user logged off intentionally
        # TODO: handle disconnection from active game...remove the player? what
        # could use reason.SERVER_DISCONNECT to detect when server kicks due to inactivity
        if reason == SocketIO.reason.CLIENT_DISCONNECT:
            if room:
                games[room].remove(username)
                emit("error", {"message": f"User {username} logged off"}, to=room)
                leave_room(room)
            del connected_users[request.sid]
        
        # if they logged off, hopefully with the intent to reconnect...
        # TODO: should implement some sort of timer to eventually remove them from connected_users and games
        else:
            emit("error", {"message": f"User {username} disconnected :("}, to=room)
    except AttributeError as e:
        print(e)

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
    
    connected_users[request.sid] = {"username": username, "game_id": game_id}
    games[game_id] = {"host" : username, "players": [username]}
    join_room(game_id)
    emit("game_created", {"game_id": game_id, "host": username}, broadcast=True) # all players can see
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

@socketio.on("start_game")
def handle_start_game(data):
    """Host starts the game, and hands are dealt."""
    username = connected_users[request.sid]["username"]
    game_id = data.get("game_id")
    if game_id not in games or games[game_id]["host"] != username:
        emit("error", {"message": "You are not the host or game does not exist."})
        return

    player_names = games[game_id]["players"]

    if len(player_names) < 2:
        emit("error", {"message": "At least 2 players needed to start!"})
        return
    
    poker_players = []
    # create Player objects
    for username in player_names:
        try:
            user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
            new_player = Player(username, user.chips)
            poker_players.append(new_player)
        except Exception as e:
            emit("error", {"message": str(e)})
            return

    game = PokerRound(poker_players, small_blind=5, big_blind=10)
    game.deal_hands_and_take_blinds()
    games[game_id]["game"] = game
    emit("game_started", {"message": "Game started successfully"}, to=game_id)

@socketio.on("get_hand")
def handle_get_hand():
    username = connected_users.get(request.sid).get("username")
    game_id = connected_users.get(request.sid).get("game_id")
    if not (username and game_id):
        emit("error", {"message": "Could not find the user in active users"})
        return

    game = games[game_id]["game"]
    hand = game.get_player_hand(username)
    return hand

@socketio.on("get_games")
def handle_get_games():
    return [{"game_id" : game_id, "host": games[game_id]["host"]} for game_id in games]

@socketio.on("check_in")
def handle_check_in():
    emit("checked_in", {"message" : "this worked"})
    print(f"got called by {request.sid}")

############################# AUTHENTICATION ##########################################

######################### UTIL METHODS ######################################

# with app.test_request_context():
#     print(url_for('hello_world'))
#     print(url_for('hello_you', name='John Doe'))
