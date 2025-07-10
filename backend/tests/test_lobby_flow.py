
import pytest
from unittest.mock import patch, MagicMock
from app.sockets import lobby_flow
from app.globals import StatusEnum

class TestValidateJoinGame:
    def test_validate_join_game_invalid_game(self, mocker):
        mocker.patch("app.sockets.lobby_flow.state.check_game_id", return_value=False)
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        result = lobby_flow.validate_join_game("game_1", None, "bob")
        
        assert result is False
        mock_emit.assert_called_with("error", {"message": "Game not found!"})

    def test_validate_join_game_already_in_game(self, mocker):
        mocker.patch("app.sockets.lobby_flow.state.check_game_id", return_value=True)
        mocker.patch("app.sockets.lobby_flow.state.get_players", return_value=["bob"])
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        result = lobby_flow.validate_join_game("game_1", None, "bob")
        
        assert result is False
        mock_emit.assert_called_with("error", {"message": "You are already in this game!"})

    def test_validate_join_game_in_another_game(self, mocker):
        mocker.patch("app.sockets.lobby_flow.state.check_game_id", return_value=True)
        mocker.patch("app.sockets.lobby_flow.state.get_players", return_value=["alice"])
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        result = lobby_flow.validate_join_game("game_1", "game_2", "bob")
        
        assert result is False
        mock_emit.assert_called_with("error", {"message": "You are already in another game!"})

    def test_validate_join_game_not_enough_bankroll(self, mocker):
        mocker.patch("app.sockets.lobby_flow.state.check_game_id", return_value=True)
        mocker.patch("app.sockets.lobby_flow.state.get_players", return_value=["alice"])
        mocker.patch("app.sockets.lobby_flow.get_user_bankroll", return_value=50)
        mocker.patch("app.sockets.lobby_flow.state.get_buy_in", return_value=100)
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        result = lobby_flow.validate_join_game("game_1", None, "bob")

        assert result is False
        mock_emit.assert_called_with("error", {"message": "You don't have enough to buy in to this game..."})

    def test_validate_join_game_success(self, mocker):
        mocker.patch("app.sockets.lobby_flow.state.check_game_id", return_value=True)
        mocker.patch("app.sockets.lobby_flow.state.get_players", return_value=["alice"])
        mocker.patch("app.sockets.lobby_flow.get_user_bankroll", return_value=150)
        mocker.patch("app.sockets.lobby_flow.state.get_buy_in", return_value=100)

        result = lobby_flow.validate_join_game("game_1", None, "bob")

        assert result is True

class TestValidateCreateGame:
    def test_validate_create_game_already_exists(self, mocker):
        mocker.patch("app.sockets.lobby_flow.state.check_game_id", return_value=True)
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        result = lobby_flow.validate_create_game("game_bob", "bob", 100)

        assert result == "game_bob"
        mock_emit.assert_called_with("error", {"message": "You have already created a game."})


    def test_validate_create_game_not_enough(self, mocker):
        mocker.patch("app.sockets.lobby_flow.state.check_game_id", return_value=False)
        mocker.patch("app.sockets.lobby_flow.get_user_bankroll", return_value=50)
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        result = lobby_flow.validate_create_game("game_bob", "bob", 100)

        assert result == ""
        mock_emit.assert_called_with("error", {"message": "You don't have enough to buy in to your own game..."})

    def test_validate_create_game_success(self, mocker):
        mocker.patch("app.sockets.lobby_flow.state.check_game_id", return_value=False)
        mocker.patch("app.sockets.lobby_flow.get_user_bankroll", return_value=200)

        result = lobby_flow.validate_create_game("game_bob", "bob", 100)

        assert result is True

class TestValidateReconnectToGame:
    @patch("app.sockets.lobby_flow.state")
    @patch("app.sockets.lobby_flow.emit")
    def test_validate_reconnect_to_game_success(self, mock_emit, mock_state):
        mock_state.check_game_id.return_value = True
        mock_state.get_players.return_value = ["alice"]
        result = lobby_flow.validate_reconnect_to_game("game_1", "game_1", "alice")
        assert result is True
        mock_emit.assert_not_called()

    @patch("app.sockets.lobby_flow.state")
    @patch("app.sockets.lobby_flow.emit")
    def test_validate_reconnect_to_game_wrong_game(self, mock_emit, mock_state):
        mock_state.check_game_id.return_value = True
        result = lobby_flow.validate_reconnect_to_game("game_1", "game_2", "alice")
        assert result is False
        mock_emit.assert_called_once()

    @patch("app.sockets.lobby_flow.state")
    @patch("app.sockets.lobby_flow.emit")
    def test_validate_reconnect_to_game_not_in_game(self, mock_emit, mock_state):
        mock_state.check_game_id.return_value = True
        mock_state.get_players.return_value = ["bob"]
        result = lobby_flow.validate_reconnect_to_game("game_1", "game_1", "alice")
        assert result is False
        mock_emit.assert_called_once()

class TestValidateLeaveGame:

    def test_invalid_game_id_emits_error(self, mocker):
        mock_state = mocker.patch("app.sockets.lobby_flow.state")
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        mock_state.check_game_id.return_value = False

        lobby_flow.validate_leave_game("game1", "bob")

        mock_emit.assert_called_once_with("error", {"message": "Game not found!"})

    def test_user_not_in_game_emits_error(self, mocker):
        mock_state = mocker.patch("app.sockets.lobby_flow.state")
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        mock_state.check_game_id.return_value = True
        mock_state.get_players.return_value = ["alice"]
        mock_state.get_joiner_queue.return_value = ["charlie"]

        lobby_flow.validate_leave_game("game1", "bob")

        mock_emit.assert_called_once_with(
            "error", {"message": "You aren't even in this game...how did you leave it??"}
        )

    def test_valid_leave_does_not_emit_error(self, mocker):
        mock_state = mocker.patch("app.sockets.lobby_flow.state")
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        mock_state.check_game_id.return_value = True
        mock_state.get_players.return_value = ["bob"]
        mock_state.get_joiner_queue.return_value = []

        lobby_flow.validate_leave_game("game1", "bob")

        mock_emit.assert_not_called()

class TestLeaveGame:

    def test_user_not_in_players_or_game_removes_from_join_queue(self, mocker):
        mock_state = mocker.patch("app.sockets.lobby_flow.state")
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        # Setup
        mock_state.get_game.return_value = None
        mock_state.get_players.return_value = []
        mock_state.get_user_sid.return_value = "sid123"

        lobby_flow.leave_game("game1", "bob")

        mock_state.set_connected_user.assert_called_once_with(None, "bob", "sid123")
        mock_state.remove_from_joiner_queue.assert_called_once_with("game1", "bob")
        mock_emit.assert_called_once_with("player_dequeued", {"game_id": "game1", "username": "bob"}, broadcast=True)

    def test_user_in_players_and_no_game_removes_from_players(self, mocker):
        mock_state = mocker.patch("app.sockets.lobby_flow.state")
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        mock_state.get_game.return_value = None
        mock_state.get_players.return_value = ["bob"]
        mock_state.get_user_sid.return_value = "sid123"

        lobby_flow.leave_game("game1", "bob")

        mock_state.set_connected_user.assert_called_once_with(None, "bob", "sid123")
        mock_state.remove_from_players.assert_called_once_with("game1", "bob")
        mock_emit.assert_called_once_with("player_left", {"game_id": "game1", "username": "bob"}, broadcast=True)

    def test_user_queued_to_leave_and_between_hands_calls_cashout(self, mocker):
        mock_state = mocker.patch("app.sockets.lobby_flow.state")
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")
        mock_cashout = mocker.patch("app.sockets.lobby_flow.cashout_and_remove_player")

        mock_state.get_game.return_value = True
        mock_state.get_players.return_value = ["bob"]
        mock_state.get_game_status.return_value = StatusEnum.between_hands.value

        lobby_flow.leave_game("game1", "bob")

        mock_state.append_to_leaver_queue.assert_called_once_with("game1", "bob")
        mock_cashout.assert_called_once_with("game1", "bob")
        mock_emit.assert_called_once_with("error", {"message": "User bob left the game!"}, to="game1")

    def test_user_leaving_during_game_but_not_between_hands(self, mocker):
        mock_state = mocker.patch("app.sockets.lobby_flow.state")
        mock_emit = mocker.patch("app.sockets.lobby_flow.emit")

        mock_state.get_game.return_value = True
        mock_state.get_players.return_value = ["bob"]
        mock_state.get_game_status.return_value = StatusEnum.in_progress.value

        lobby_flow.leave_game("game1", "bob")

        mock_state.append_to_leaver_queue.assert_called_once_with("game1", "bob")
        mock_emit.assert_called_once_with("error", {"message": "User bob left the game!"}, to="game1")