from flask import request
from flask_socketio import emit
from app.extensions import socketio
from app.globals import connected_users, games
from app.db import db
from app.models.user import User
from app.game_logic.game_logic import PokerRound, Player

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