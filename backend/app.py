from datetime import datetime, timedelta, timezone
from flask import Flask, request, session, jsonify
from flask_jwt_extended import create_access_token, current_user, decode_token, get_csrf_token, get_jwt, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, unset_jwt_cookies
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from game.game import PokerRound, Player
from db import init_db, db, User
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# CORS
app.secret_key = "secret_sauce@45*"
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})

# db - see db.py
init_db(app)

# jwt (auth)
app.config["JWT_SECRET_KEY"] = "Bru5$j^yeah"
app.config["JWT_COOKIE_SECURE"] = False # DEBUG ONLY: set true when released
app.config["JWT_COOKIE_SAMESITE"] = "Lax" # required for cookie inclusing in requests between diff domains
app.config["JWT_CSRF_IN_COOKIES"] = True # send the csrf token via cookie so that the frontend can grab from browser
app.config["JWT_TOKEN_LOCATION"] = ["cookies"] # allows jwt in http-only cookie (protect against XSS attack)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# sockets (game state)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    game.deal_hands()
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

# DEBUG ONLY: print db contents
@app.route("/")
def hello_world():
    users = db.session.execute(db.select(User)).scalars().all()
    users_string = ("\n").join([f"<h1>{user.to_dict()}</h1>" for user in users])
    return f"<h1>users: \n{users_string}</h1>\n<h2>session: {session}</h2>"

############################# AUTHENTICATION ##########################################

# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user):
    try:
        return str(user.id)
    except AttributeError:
        print(f"user is {user}")


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    user = db.session.execute(db.select(User).filter_by(username=data["username"])).scalar_one_or_none()
    if not user:
        return jsonify({"error": "Username not found"}), 404
    if not user.check_password(data["password"]):
        return jsonify({"error": "Incorrect password"}), 401
    
    # TODO TOKEN
    access_token = create_access_token(identity=user) # can pass user object due to jwt.user_identity_loader
    response = jsonify({"message": "Login successful from backend"})
    try:
        set_access_cookies(response, access_token)
    except Exception as e:
        print(f"error: {e}")
        return jsonify({"error": "server-side"}), 500
    return response

@app.route("/auth/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful from backend"})
    unset_jwt_cookies(response)
    return response

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    new_usr = User(data["username"], data["chips"], data["password"]) 
    try:
        db.session.add(new_usr)
        db.session.commit()    
    except IntegrityError as e:
        return jsonify({"error": "Username taken"}), 500

    # TODO TOKEN - OR MAYBE NOT - make the user enter their new details to login
    # access_token = create_access_token(identity=data["username"])
    response = jsonify({"message": "Registration successful from backend"})
    # try:
    #     set_access_cookies(response, access_token)
    # except Exception as e:
    #     print(f"error: {e}")
    #     return jsonify({"error": "server-side"}), 500
    return response

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/auth/who_am_i", methods=["POST"])
@jwt_required()
def who_am_i():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify({"user": current_user.to_dict()})

######################### UTIL METHODS ######################################

@app.route("/make-sol", methods=["GET"])
def add_user():
    new_usr = User("kenna", 1000, "ilovemybf") # soljt password: pass
    db.session.add(new_usr)
    db.session.commit()
    return f"<h1>SUCCESS</h1>"

@app.route("/delete-users", methods=["GET"])
def delete_users():
    users = db.session.execute(db.select(User).filter(User.username.not_in(["soljt", "kenna"]))).scalars().fetchall()
    for user in users:
        db.session.delete(user)
    
    db.session.commit()
    # db.session.commit()
    return f"<h1>DELETED USERS:</h1>\n{"".join(f"<p>{user.username}</p>\n" for user in users)}"


# @app.route("/<name>")
# def hello_you(name):
#     return f"<h1>this is nuts and insane lmao. your name: {name} </p>"

# with app.test_request_context():
#     print(url_for('hello_world'))
#     print(url_for('hello_you', name='John Doe'))

# game_state = {"round": None}

# @app.route("/start_game", methods=["POST"])
# def start_game():
#     """Initialize a new round of poker."""
#     game_state["round"] = PokerRound()
#     return jsonify({"message": "Game started!"})

# @app.route("/play", methods=["POST"])
# def play_round():
#     """Execute a round of poker."""
#     if game_state["round"]:
#         game_state["round"].play()
#         return jsonify({"message": "Round played!"})
#     return jsonify({"error": "No game started"}), 400

if __name__ == "__main__":
    socketio.run(app, debug=True)