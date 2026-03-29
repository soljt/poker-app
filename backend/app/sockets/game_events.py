from flask import request
from flask_socketio import emit
from app.extensions import socketio
import app.state as state
from app.sockets.helpers import validate_player, get_user_bankroll, update_player_chips
from app.sockets.game_flow import handle_player_action_helper, handle_start_game_helper

@socketio.on("start_game")
def handle_start_game(data):
    """Host starts the game, and hands are dealt."""
    username, _ = validate_player(request)
    game_id = data.get("game_id")
    if not state.check_game_id(game_id) or state.get_host(game_id) != username:
        emit("error", {"message": "You are not the host or game does not exist."})
        return

    player_names = state.get_players(game_id)
    if len(player_names) < 2:
        emit("error", {"message": "At least 2 players needed to start!"})
        return
    
    handle_start_game_helper(game_id)

@socketio.on("player_action")
def handle_player_action(data):
    try:
        username, game_id = validate_player(request)            
        print(f"data received on player {username} action:", data)
        handle_player_action_helper(username, game_id, data.get("action"), data.get("amount"))
        
    except Exception as e:
        emit("error", {"message": str(e)})
        return

@socketio.on("get_hand")
def handle_get_hand():
    username, game_id = validate_player(request)

    game = state.get_game(game_id)
    hand = game.get_player_hand(username)
    return hand

@socketio.on("reveal_hand")
def handle_reveal_hand():
    username, game_id = validate_player(request)

    game = state.get_game(game_id)
    hand = game.get_player_hand(username)
    emit("hand_revealed", {"username": username, "hand": hand}, to=game_id)

@socketio.on("reveal_bot_hand")
def handle_reveal_bot_hand():
    from app.sockets.game_flow import emit_bot_hands
    _, game_id = validate_player(request)
    emit_bot_hands(game_id)

@socketio.on("rebuy")
def handle_rebuy():
    try:
        username, game_id = validate_player(request)

        if username not in state.get_rebuy_queue(game_id):
            emit("error", {"message": "You are not eligible for a rebuy."})
            return

        buy_in = state.get_buy_in(game_id)
        bankroll = get_user_bankroll(username)

        if bankroll < buy_in:
            emit("error", {"message": f"Not enough chips in your wallet to rebuy (need {buy_in})."})
            return

        update_player_chips(username, bankroll - buy_in)
        state.get_game(game_id).get_player(username).chips += buy_in
        state.remove_from_rebuy_queue(game_id, username)

        emit("rebuy_confirmed", {"buy_in": buy_in})
        emit("chips_updated")
    except Exception as e:
        emit("error", {"message": str(e)})