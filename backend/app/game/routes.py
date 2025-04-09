from flask import jsonify, request
from flask_jwt_extended import current_user, jwt_required
from app.game import game
from app.globals import games

@game.route("/state", methods=["GET"])
@jwt_required()
def get_game_state():
    game_id = request.args.get("game_id")
    username = current_user.username

    if not game_id in games:
        return jsonify({"error": "Game does not exist."})
    
    if not games[game_id].get("game"):
        return jsonify({"error": "Game has not started - no game object."})
    
    if not username in games.get(game_id).get("players"):
        return jsonify({"error": f"Could not find user {username} in player list for game_id {game_id}."})
    
    response = games[game_id]["game"].serialize_for_player(username)
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

    if not game_id in games:
        return jsonify({"error": "Game does not exist."})
    
    if not username in games.get(game_id).get("players"):
        return jsonify({"error": f"Could not find user {username} in player list for game_id {game_id}."})
    
    response = {"host": games[game_id]["host"]}
    try:
        response = jsonify(response)
    except Exception as e:
        print("\n\nERROR FROM GET GAME STATE")
        print(e)
        print("\n\n")
        return jsonify({"error", "not serializeable"})
    
    return response
    