import pytest
import app.state as state
from app.globals import games, user_sids, connected_users
from app.sockets import helpers


@pytest.fixture(autouse=True)
def clean_state(mocker):
    games.clear(); user_sids.clear(); connected_users.clear()
    mocker.patch.object(helpers, "socketio")
    yield
    games.clear(); user_sids.clear(); connected_users.clear()


def test_in_started_game_is_busy():
    state.set_new_game_id("g1", "host", 10, 20, 1000)
    state.append_to_players("g1", "Demo Dan")
    assert not helpers.is_in_started_game("Demo Dan")
    state.set_game("g1", object())
    assert helpers.is_in_started_game("Demo Dan")


def test_evict_removes_from_waiting_lobby_and_drops_socket():
    state.set_new_game_id("g1", "host", 10, 20, 1000)
    state.append_to_players("g1", "Demo Dan")
    state.set_user_sid("Demo Dan", "sid1")
    state.set_connected_user("g1", "Demo Dan", "sid1")

    helpers.evict_user("Demo Dan")

    assert state.get_players("g1") == ["host"]
    assert state.get_user_sid("Demo Dan") == ""
    assert "sid1" not in connected_users
    helpers.socketio.server.disconnect.assert_called_once_with("sid1", namespace="/")


def test_evict_deletes_hosted_lobby(mocker):
    delete_game = mocker.patch.object(helpers, "delete_game")
    state.set_new_game_id("g1", "Demo Dan", 10, 20, 1000)
    helpers.evict_user("Demo Dan")
    delete_game.assert_called_once_with("g1")


def test_evict_dequeues_from_started_game():
    state.set_new_game_id("g1", "host", 10, 20, 1000)
    state.set_game("g1", object())
    state.append_to_joiner_queue("g1", "Demo Dan")
    helpers.evict_user("Demo Dan")
    assert state.get_joiner_queue("g1") == []
