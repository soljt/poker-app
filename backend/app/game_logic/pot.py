from __future__ import annotations
import sys
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.game_logic.player import Player


class Pot:
    def __init__(self) -> None:
        self.player_contributions: dict = {}  # {player: contribution}
        self.amount: int = 0
        self.next: Optional[Pot] = None
        self.contribution_limit: int = sys.maxsize
        self.max_seen_contribution: int = 0

    def add(self, player: Player, amount_to_add: int, allin: bool = False) -> int:
        """
        Add a player contribution to this pot. Returns any remainder that
        overflows the contribution limit (to be added to the next pot).
        """
        old_contribution = self.player_contributions.get(player, 0)

        if old_contribution + amount_to_add > self.contribution_limit:
            self.amount += self.contribution_limit - old_contribution
            self.player_contributions[player] = self.contribution_limit
            return amount_to_add - (self.contribution_limit - old_contribution)

        self.amount += amount_to_add
        self.player_contributions[player] = old_contribution + amount_to_add

        if self.player_contributions[player] > self.max_seen_contribution:
            self.max_seen_contribution = self.player_contributions[player]
        if allin:
            self.contribution_limit = self.player_contributions[player]
        return 0

    def award_pot(
        self,
        ranked_active_players: List[List[Player]],
        active_players: set = set(),
        player_hands: dict = {},
    ) -> tuple[dict, dict]:
        """
        Award this pot to the best-handed eligible player(s).

        Returns (award_info, chip_changes) where chip_changes maps
        Player → chips to add. Caller applies chip_changes to Player objects.
        """
        group_idx = 0
        winners = [p for p in ranked_active_players[group_idx] if p in self.player_contributions]
        while not winners:
            group_idx += 1
            winners = [p for p in ranked_active_players[group_idx] if p in self.player_contributions]

        share = self.amount // len(winners)
        amount = self.amount = share * len(winners)

        print(f"------------- WITHIN POT ------------")
        print(f"splitting {self.amount} among {winners}")
        chip_changes: dict = {}
        for player in winners:
            self.amount -= share
            chip_changes[player] = share
            print(f"{player} gets {share}")
        print(f"-------------------------")

        pot_players = set(self.player_contributions)
        must_show = len(pot_players.intersection(active_players)) != 1
        hand_rank = player_hands[winners[0]].hand_rank.label if must_show else "By Default"

        award_info = {
            "winners": [w.name for w in winners],
            "amount": amount,
            "share": share,
            "hand_rank": hand_rank,
            "must_show": must_show,
        }
        return award_info, chip_changes

    def refund_pot(self) -> dict:
        """Return contributions to each player. Returns chip_changes map."""
        if self.amount == 0:
            return {}
        chip_changes: dict = {}
        for player in self.player_contributions:
            chip_changes[player] = self.player_contributions[player]
            self.amount -= self.player_contributions[player]
            self.player_contributions[player] = 0
        return chip_changes

    def serialize(self) -> dict:
        return {
            "amount": self.amount,
            "players": [str(p) for p in self.player_contributions],
        }

    def __repr__(self) -> str:
        return f"POT:\n{self.amount}\n{[(p.name, self.player_contributions[p]) for p in self.player_contributions]}"


class PotCollection:
    def __init__(self) -> None:
        self.main_pot = Pot()
        self.current_pot = self.main_pot

    def add_contribution(self, player: Player, amount_to_add: int) -> None:
        """Add a player contribution, splitting across pots as needed."""
        pot = self.current_pot
        remainder = pot.add(player, amount_to_add, player.allin)
        while remainder:
            if not pot.next:
                pot.next = Pot()
            pot = pot.next
            remainder = pot.add(player, remainder, player.allin)
        if pot.max_seen_contribution > pot.contribution_limit:
            self.restructure_pot(pot)

    def restructure_pot(self, pot: Pot) -> None:
        """
        Cap this pot at its contribution_limit and move any excess to a new side pot.
        Called when a player calls all-in for less than the current bet.
        """
        temp = pot.next
        pot.next = Pot()
        pot.next.next = temp

        for player in pot.player_contributions:
            surplus = pot.player_contributions[player] - pot.contribution_limit
            if surplus > 0:
                pot.player_contributions[player] -= surplus
                pot.amount -= surplus
                pot.next.add(player, surplus, player.allin)

        pot.max_seen_contribution = pot.contribution_limit

    def end_betting_round(self) -> dict:
        """
        Clean up garbage pots (uncalled bets) and advance current_pot pointer.
        Returns chip_changes for any refunded garbage pot contributions.
        """
        prev = curr = self.current_pot
        while curr.next:
            prev = curr
            curr = curr.next

        chip_changes: dict = {}
        if len(curr.player_contributions) <= 1:
            print(f"COLLECTING GARBAGE:\nPOT: {curr} dies now\n")
            for player in curr.player_contributions:
                chip_changes[player] = curr.amount
            prev.next = None
            curr = prev

        self.current_pot = curr
        return chip_changes

    def award_pot(
        self,
        ranked_active_players: List[List[Player]],
        active_players: set = set(),
        player_hands: dict = {},
    ) -> tuple[list, dict]:
        """
        Award all pots. Returns (pot_award_info_list, aggregated_chip_changes).
        Caller applies chip_changes to Player objects.
        """
        print(f"----------------------POT COLLECTION--------------------------")
        pot_award_info = []
        all_chip_changes: dict = {}
        pot = self.main_pot
        while pot:
            info, chip_changes = pot.award_pot(ranked_active_players, active_players, player_hands)
            pot_award_info.append(info)
            for player, amount in chip_changes.items():
                all_chip_changes[player] = all_chip_changes.get(player, 0) + amount
            pot = pot.next
        print("-" * 80)
        return pot_award_info, all_chip_changes

    def refund_pot(self) -> dict:
        """Refund all pots. Returns aggregated chip_changes map."""
        all_chip_changes: dict = {}
        pot = self.main_pot
        while pot:
            for player, amount in pot.refund_pot().items():
                all_chip_changes[player] = all_chip_changes.get(player, 0) + amount
            pot = pot.next
        return all_chip_changes

    def __repr__(self) -> str:
        curr = self.main_pot
        parts = []
        while curr:
            parts.append(repr(curr))
            curr = curr.next
            if curr:
                parts.append("\n|\n|\n|\nv\n")
        return "".join(parts)
