from flask import Flask, request, session, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from game.game import PokerRound, Player  # Import your PokerRound logic
from db import init_db, db, User

app = Flask(__name__)
app.secret_key = "secret_sauce@45*"
CORS(app, supports_credentials=True)  # Allow frontend to access backend
init_db(app)
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}  # Store players: {"username": Player}
game = None   # Store the game instance


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
    join_room(username)  # Creates a private "room" for this player
    
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

    # Send each player their own hand
    for username, player in players.items():
        cards = [str(card) for card in player.hole_cards]
        emit("your_hand", {"cards": cards}, room=username)
        print(cards)

@socketio.on("check_in")
def handle_check_in():
    emit("checked_in", {"message" : "this worked"})

@app.route("/")
def hello_world():
    users = db.session.execute(db.select(User)).scalars().all()
    users_string = ("\n").join([f"<h1>{user.to_dict()}</h1>" for user in users])
    return f"<h1>users: \n{users_string}</h1>\n<h2>session: {session}</h2>"

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = db.session.execute(db.select(User).filter_by(username=data["username"])).scalar_one_or_none()
    if not user:
        return jsonify({"error": "Username not found"}), 404
    if not user.check_password(data["password"]):
        return jsonify({"error": "Incorrect password"}), 401
    
    # TODO TOKEN
    session["user"] = user.to_dict()
    return jsonify(session["user"])

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    new_usr = User(data["username"], data["chips"], data["password"]) 
    db.session.add(new_usr)
    db.session.commit()    

    # TODO TOKEN
    session["user"] = user.to_dict()
    return jsonify(session["user"])

@app.route("/user")
def user():
    if "user" not in session:
        user = db.session.execute(db.select(User).filter_by(id=request.args.get("userId"))).scalar_one_or_none()
        if not user:
            return jsonify({"error": "User does not exist"})
        session["user"] = user.to_dict()
    return jsonify(session["user"])


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