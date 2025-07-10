from flask import jsonify, request
from flask_jwt_extended import current_user, jwt_required
from app.game import game
import app.state as state

@game.route("/state", methods=["GET"])
@jwt_required()
def get_game_state():
    game_id = request.args.get("game_id")
    username = current_user.username

    if not state.check_game_id(game_id):
        return jsonify({"error": "Game does not exist."})
    
    if not state.get_game(game_id):
        return jsonify({"error": "Game has not started - no game object."})
    
    if not username in state.get_players(game_id):
        return jsonify({"error": f"Could not find user {username} in player list for game_id {game_id}."})
    
    response = state.get_game(game_id).serialize_for_player(username)
    try:
        response = jsonify(response)
    except Exception as e:
        print("\n\nERROR FROM GET GAME STATE")
        print(e)
        print("\n\n")
        return jsonify({"error", "not serializeable"})
    
    return response

@game.route("/host", methods=["GET"])
@jwt_required()
def get_game_host():
    game_id = request.args.get("game_id")
    username = current_user.username

    if not state.check_game_id(game_id) or not username in state.get_players(game_id):
        return jsonify({"error": "Could not retrieve host"})
    
    response = {"host": state.get_host(game_id)}
    try:
        response = jsonify(response)
    except Exception as e:
        print("\n\nERROR FROM GET GAME STATE")
        print(e)
        print("\n\n")
        return jsonify({"error", "not serializeable"})
    
    return response
    