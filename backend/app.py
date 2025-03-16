from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from game.game import PokerRound, Player  # Import your PokerRound logic
from flask import url_for

app = Flask(__name__)
CORS(app)  # Allow frontend to access backend
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
        emit("your_hand", {"cards": [str(card) for card in player.hole_cards]}, room=username)



@app.route("/")
def hello_world():
    return f"<h1>hello world</h1>"

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