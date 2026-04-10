from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.game_logic.card import Card


class Player:
    def __init__(self, name: str, chips: int = 1000) -> None:
        self.name = name
        self.chips = chips
        self.hole_cards: List[Card] = []
        self.current_bet = 0
        self.playing = True
        self.folded = False
        self.allin = False

    def bet(self, amount: int) -> int:
        """
        Bet the specified amount — deduct it from chips and update current_bet.
        If amount exceeds available chips, the player goes all-in.
        Returns the amount added to the pot.
        """
        if amount > self.chips + self.current_bet:
            amount = self.chips + self.current_bet

        amount_to_add_to_pot = amount - self.current_bet
        self.chips -= amount_to_add_to_pot
        self.current_bet = amount
        if self.chips == 0:
            self.allin = True
        return amount_to_add_to_pot

    def reset(self) -> None:
        """Prepare player for a new poker round."""
        self.current_bet = 0
        self.folded = False
        self.allin = False
        self.hole_cards = []

    def __repr__(self) -> str:
        return f"{self.name}"
