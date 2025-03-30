from datetime import datetime, timedelta, timezone
from flask import Flask, request, session, jsonify
from flask_jwt_extended import create_access_token, current_user, get_csrf_token, get_jwt, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, unset_jwt_cookies
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from game.game import PokerRound, Player
from db import init_db, db, User

app = Flask(__name__)

# CORS
app.secret_key = "secret_sauce@45*"
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})

# db - see db.py
init_db(app)

# jwt (auth)
app.config["JWT_SECRET_KEY"] = "Bru5$j^yeah"
app.config["JWT_COOKIE_SECURE"] = False # DEBUG ONLY: set true when released
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_CSRF_IN_COOKIES"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# sockets (game state)
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}
game = None

@socketio.on("join")
def handle_join(data):
    """Handles when a user joins the game by submitting their username and chips."""
    username = data["username"]
    chips = data["chips"]
    
    if username in players:
        emit("error", {"message": "Username already taken"})
        return
    
    new_player = Player(username, chips)
    players[username] = new_player
    join_room(username)
    
    emit("joined", {"message": f"Welcome, {username}!"}, room=username)


@socketio.on("start_game")
def handle_start_game():
    """Host starts the game, and hands are dealt."""
    global game
    if len(players) < 2:
        emit("error", {"message": "At least 2 players needed to start!"})
        return

    game = PokerRound(list(players.values()), small_blind=5, big_blind=10)
    game.deal_hands()

    for username, player in players.items():
        cards = [str(card) for card in player.hole_cards]
        emit("your_hand", {"cards": cards}, room=username)
        print(cards)

@socketio.on("check_in")
def handle_check_in():
    emit("checked_in", {"message" : "this worked"})

# DEBUG ONLY: print db contents
@app.route("/")
def hello_world():
    users = db.session.execute(db.select(User)).scalars().all()
    users_string = ("\n").join([f"<h1>{user.to_dict()}</h1>" for user in users])
    return f"<h1>users: \n{users_string}</h1>\n<h2>session: {session}</h2>"

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
    return str(user.id)

# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = db.session.execute(db.select(User).filter_by(username=data["username"])).scalar_one_or_none()
    if not user:
        return jsonify({"error": "Username not found"}), 404
    if not user.check_password(data["password"]):
        return jsonify({"error": "Incorrect password"}), 401
    
    # TODO TOKEN
    access_token = create_access_token(identity=user) # can pass user object due to jwt.user_identity_loader
    csrf = get_csrf_token(access_token)
    response = jsonify({"message": "Login successful from backend", "token": csrf})
    try:
        set_access_cookies(response, access_token)
    except Exception as e:
        print(f"error: {e}")
        return jsonify({"error": "server-side"}), 500
    return response

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful from backend"})
    unset_jwt_cookies(response)
    return response

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    new_usr = User(data["username"], data["chips"], data["password"]) 
    db.session.add(new_usr)
    db.session.commit()    

    # TODO TOKEN
    access_token = create_access_token(identity=data["username"])
    return jsonify(access_token=access_token)

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/who_am_i", methods=["POST"])
@jwt_required()
def who_am_i():
    # We can now access our sqlalchemy User object via `current_user`.
    print(request.json)
    return jsonify({"user": current_user.to_dict()})


@app.route("/make-sol", methods=["GET"])
def add_user():
    new_usr = User("kenna", 1000, "ilovemybf") # soljt password: pass
    db.session.add(new_usr)
    db.session.commit()
    return f"<h1>SUCCESS</h1>"


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