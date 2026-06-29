from __future__ import annotations
import random
from dataclasses import dataclass
from typing import ClassVar, List

from app.game_logic.enums import Rank, Suit


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    # Class-level lists kept for backward-compatible index lookups (e.g. RANKS.index("A"))
    RANKS: ClassVar[List[Rank]] = list(Rank)
    SUITS: ClassVar[List[Suit]] = list(Suit)

    def __post_init__(self) -> None:
        # Coerce plain strings so Card("A", "spades") still works
        if not isinstance(self.rank, Rank):
            object.__setattr__(self, "rank", Rank(self.rank))
        if not isinstance(self.suit, Suit):
            object.__setattr__(self, "suit", Suit(self.suit))

    def __lt__(self, other: Card) -> bool:
        return Card.RANKS.index(self.rank) < Card.RANKS.index(other.rank)

    def __repr__(self) -> str:
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self) -> None:
        self.cards: List[Card] = [Card(rank, suit) for rank in Rank for suit in Suit]
        random.shuffle(self.cards)

    def deal(self, hand_size: int) -> List[Card]:
        if len(self.cards) >= hand_size:
            return [self.cards.pop() for _ in range(hand_size)]
        raise Exception("DECK EMPTY")

    def __repr__(self) -> str:
        return f"{', '.join(map(str, self.cards))}"
