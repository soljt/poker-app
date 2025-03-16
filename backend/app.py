from flask import Flask, jsonify, request
from flask_cors import CORS
from game.game import PokerRound  # Import your PokerRound logic
from flask import url_for

app = Flask(__name__)
CORS(app)  # Allow frontend to access backend


# @app.route("/")
# def hello_world():
#     return f"<h1>hello world</p>"

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
    app.run(debug=True)