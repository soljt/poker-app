import random
from abc import ABC, abstractmethod


class DecisionEngine(ABC):
    @abstractmethod
    def decide(self, game_state: dict, available_actions: list[dict]) -> tuple[str, int | None]:
        """
        Choose a poker action given the current game state.

        Args:
            game_state: serialized game state from PokerRound.serialize_for_player(), containing:
                - "my_cards":    list[str]  — hole cards, e.g. ["A of spades", "K of hearts"]
                - "board":       list[str]  — community cards (0-5)
                - "players":     list[dict] — [{"username", "chips", "folded", "current_bet"}, ...]
                - "pots":        list[dict] — [{"amount": int, "players": list[str]}, ...]
                - "blinds":      [int, int] — [small_blind, big_blind]
                - "my_chips":    int        — bot's remaining stack
                - "my_bet":      int        — bot's current bet this round
                - "table_bet":   int        — highest bet on the table
                - "phase":       str        — "preflop" | "flop" | "turn" | "river"

            available_actions: list of action dicts, e.g.:
                [{"action": "call", "min": None, "allin": False},
                 {"action": "raise", "min": 40, "allin": False},
                 {"action": "fold", "min": None, "allin": False}]
                valid action strings: "fold", "check", "call", "bet", "raise", "reraise"

        Returns:
            (action, amount) where:
                - action is a string present in available_actions
                - amount is an int >= action's "min" for bet/raise/reraise, or None otherwise
        """
        pass


class RandomDecisionEngine(DecisionEngine):
    """Picks a random valid action. Used as a fallback and in tests."""

    def decide(self, game_state: dict, available_actions: list[dict]) -> tuple[str, int | None]:
        action_dict = random.choice(available_actions)
        action = action_dict["action"]
        min_amount = action_dict.get("min")
        amount = min_amount if min_amount is not None else None
        return action, amount
