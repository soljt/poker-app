from __future__ import annotations
from typing import List, Union

from app.game_logic.player import Player


class Table:
    def __init__(
        self,
        num_seats: int,
        players: Union[List[str], List[Player]],
        max_seats: int = 8,
    ) -> None:
        self.max_seats = max_seats
        # Convert name strings to Player instances if needed
        if players and isinstance(players[0], str):
            players = [Player(p) for p in players]

        self._seats: List[Player] = list(players)
        self._btn_idx: int = 0
        self.num_seats: int = len(self._seats)

    # ── position properties ──────────────────────────────────────────────────

    @property
    def btn(self) -> Player:
        return self._seats[self._btn_idx]

    @property
    def sb(self) -> Player:
        # Heads-up: btn IS sb
        if self.num_seats == 2:
            return self._seats[self._btn_idx]
        return self._seats[(self._btn_idx + 1) % self.num_seats]

    @property
    def bb(self) -> Player:
        if self.num_seats == 2:
            return self._seats[(self._btn_idx + 1) % self.num_seats]
        return self._seats[(self._btn_idx + 2) % self.num_seats]

    # ── traversal helpers (replace .left / .right) ───────────────────────────

    def next_player(self, player: Player) -> Player:
        """Player to the left — next to act in betting order."""
        idx = self._seats.index(player)
        return self._seats[(idx + 1) % self.num_seats]

    def prev_player(self, player: Player) -> Player:
        """Player to the right — used when walking backward (last-to-act after a raise)."""
        idx = self._seats.index(player)
        return self._seats[(idx - 1) % self.num_seats]

    # ── lifecycle ────────────────────────────────────────────────────────────

    def rotate(self) -> None:
        self._btn_idx = (self._btn_idx + 1) % self.num_seats

    def reset(self) -> None:
        for player in self._seats:
            player.reset()

    # ── player management ────────────────────────────────────────────────────

    def add_player(self, player: Player) -> None:
        """Insert new player at the btn position; new player becomes btn."""
        self._seats.insert(self._btn_idx, player)
        self.num_seats += 1
        # _btn_idx unchanged — it now points to the newly inserted player

    def remove_player(self, player: Player) -> None:
        idx = self._seats.index(player)
        self._seats.remove(player)
        self.num_seats -= 1

        if idx == self._btn_idx:
            # Removed player was btn; new btn is whatever is now at _btn_idx
            self._btn_idx = self._btn_idx % self.num_seats
        elif idx < self._btn_idx:
            # A player before btn was removed; shift btn index down
            self._btn_idx -= 1
        # If idx > _btn_idx, _btn_idx is unchanged

    # ── serialization ────────────────────────────────────────────────────────

    def get_players(self) -> List[str]:
        """Return player names starting from sb, ending at btn."""
        return [
            str(self._seats[(self._btn_idx + 1 + i) % self.num_seats])
            for i in range(self.num_seats)
        ]

    def get_players_info(self) -> List[dict]:
        """Return player info dicts starting from sb, ending at btn."""
        result = []
        for i in range(self.num_seats):
            p = self._seats[(self._btn_idx + 1 + i) % self.num_seats]
            result.append(
                {
                    "username": str(p),
                    "chips": p.chips,
                    "folded": p.folded,
                    "current_bet": p.current_bet,
                }
            )
        return result
