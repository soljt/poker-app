import json
import os
import uuid
import threading
from datetime import datetime, timezone


class GameRecorder:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self._in_progress: dict[str, dict] = {}
        self._lock = threading.Lock()

    def start_hand(self, game_id: str, hand_number: int, game) -> None:
        players = game.get_players()
        game_state = game.serialize_for_player(players[0])
        starting_stacks = {p: game.get_player(p).chips for p in players}
        record = {
            "hand_id": str(uuid.uuid4()),
            "game_id": game_id,
            "hand_number": hand_number,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "small_blind": game.sb_amount,
            "big_blind": game.bb_amount,
            "small_blind_player": game_state["small_blind_player"],
            "big_blind_player": game_state["big_blind_player"],
            "players_dealt_in": players,
            "starting_stacks": starting_stacks,
            "actions": [],
        }
        self._in_progress[game_id] = record

    def record_action(self, game_id: str, actor: str, action_taken: str,
                      amount: int | None, game) -> None:
        record = self._in_progress.get(game_id)
        if record is None:
            return
        game_state = game.serialize_for_player(actor)
        action_record = {
            "action_index": len(record["actions"]),
            "phase": game_state["phase"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "board": game_state["board"],
            "pots": game_state["pots"],
            "players": game_state["players"],
            "table_bet": game_state["table_bet"],
            "small_blind_player": game_state["small_blind_player"],
            "big_blind_player": game_state["big_blind_player"],
            "actor": actor,
            "actor_hole_cards": game_state["my_cards"],
            "actor_chips": game_state["my_chips"],
            "actor_current_bet": game_state["my_bet"],
            "available_actions": game_state["available_actions"],
            "action_taken": action_taken,
            "amount": amount,
        }
        record["actions"].append(action_record)

    def finish_hand(self, game_id: str, game, pot_award_info: list) -> None:
        record = self._in_progress.pop(game_id, None)
        if record is None:
            return
        showdown_entries = game.determine_must_show_players(pot_award_info)
        record["final_board"] = game.get_board()
        record["final_phase_reached"] = game.phase
        record["pot_awards"] = pot_award_info
        record["showdown_hands"] = {e["username"]: e["hand"] for e in showdown_entries}
        self._write_record(record)

    def discard_hand(self, game_id: str) -> None:
        self._in_progress.pop(game_id, None)

    def _write_record(self, record: dict) -> None:
        path = self._today_file()
        os.makedirs(self.data_dir, exist_ok=True)
        with self._lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")

    def _today_file(self) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return os.path.join(self.data_dir, f"games_{date_str}.jsonl")


recorder = GameRecorder(
    data_dir=os.environ.get(
        "GAME_DATA_DIR",
        os.path.join(os.path.dirname(__file__), "..", "..", "game_data"),
    )
)
