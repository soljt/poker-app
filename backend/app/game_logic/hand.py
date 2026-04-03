from __future__ import annotations
import itertools
from typing import List, Tuple

from app.game_logic.card import Card
from app.game_logic.enums import HandRank


class Hand:
    def __init__(self, cards: List[Card], sorted: bool = False) -> None:
        self.cards = cards
        if not sorted:
            self.cards.sort()
        self.hand_rank, self.card_ranks = self.evaluate()

    def evaluate(self) -> Tuple[HandRank, List[int]]:
        """
        Given a SORTED 5-card hand, determine the hand rank and card ranks used to
        break ties (kickers, top card of flush/straight, etc.).
        """
        suit_counts: dict = {}
        rank_counts: dict = {}

        straight = True
        ace_low_straight = False
        prev_rank_index = Card.RANKS.index(self.cards[0].rank)

        suit_counts[self.cards[0].suit] = suit_counts.get(self.cards[0].suit, 0) + 1
        rank_counts[self.cards[0].rank] = rank_counts.get(self.cards[0].rank, 0) + 1

        for i in range(1, len(self.cards)):
            if Card.RANKS.index(self.cards[i].rank) != prev_rank_index + 1:
                if Card.RANKS.index(self.cards[i].rank) == 12 and prev_rank_index == 3:
                    ace_low_straight = True
                else:
                    straight = False
            prev_rank_index = Card.RANKS.index(self.cards[i].rank)

            suit_counts[self.cards[i].suit] = suit_counts.get(self.cards[i].suit, 0) + 1
            rank_counts[self.cards[i].rank] = rank_counts.get(self.cards[i].rank, 0) + 1

        flush_suit = [s for s in suit_counts if suit_counts[s] >= 5]

        top_card_rank_index = Card.RANKS.index(self.cards[len(self.cards) - 1].rank)

        # royal flush
        if flush_suit and straight and top_card_rank_index == Card.RANKS.index("A"):
            return (HandRank.ROYAL_FLUSH, [])

        # straight flush
        if flush_suit and straight:
            if ace_low_straight:
                return (HandRank.STRAIGHT_FLUSH, [3])
            return (HandRank.STRAIGHT_FLUSH, [top_card_rank_index])

        # quads
        quads_rank = [r for r in rank_counts if rank_counts[r] == 4]
        if quads_rank:
            return (
                HandRank.QUADS,
                [Card.RANKS.index(quads_rank[0])]
                + [Card.RANKS.index(c.rank) for c in self.cards if Card.RANKS.index(c.rank) != Card.RANKS.index(quads_rank[0])],
            )

        # full house
        trips_rank = [r for r in rank_counts if rank_counts[r] == 3]
        trips_rank = Card.RANKS.index(trips_rank[0]) if trips_rank else None

        pair_ranks = [r for r in rank_counts if (rank_counts[r] == 2 and r != trips_rank)]
        if pair_ranks:
            pair_ranks = [Card.RANKS.index(pr) for pr in pair_ranks]
            pair_ranks.sort(reverse=True)

        if trips_rank is not None and pair_ranks:
            return (HandRank.FULL_HOUSE, [trips_rank, pair_ranks[0]])

        # flush
        if flush_suit:
            return (HandRank.FLUSH, [top_card_rank_index])

        # straight
        if straight:
            if ace_low_straight:
                return (HandRank.STRAIGHT, [3])
            return (HandRank.STRAIGHT, [top_card_rank_index])

        # trips
        if trips_rank is not None:
            return (
                HandRank.TRIPS,
                [trips_rank]
                + list(reversed([Card.RANKS.index(c.rank) for c in self.cards if Card.RANKS.index(c.rank) != trips_rank])),
            )

        # two pair
        if len(pair_ranks) == 2:
            return (
                HandRank.TWO_PAIR,
                pair_ranks + [Card.RANKS.index(c.rank) for c in self.cards if Card.RANKS.index(c.rank) not in pair_ranks],
            )

        # pair
        if pair_ranks:
            return (
                HandRank.PAIR,
                [pair_ranks[0]]
                + list(reversed([Card.RANKS.index(c.rank) for c in self.cards if Card.RANKS.index(c.rank) != pair_ranks[0]])),
            )

        # high card
        return (HandRank.HIGH_CARD, list(reversed([Card.RANKS.index(c.rank) for c in self.cards])))

    def __lt__(self, other: Hand) -> bool:
        if self.hand_rank == other.hand_rank:
            for i in range(len(self.card_ranks)):
                if self.card_ranks[i] < other.card_ranks[i]:
                    return True
                elif self.card_ranks[i] > other.card_ranks[i]:
                    return False
            return False
        return self.hand_rank < other.hand_rank

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        if self.hand_rank == other.hand_rank:
            for i in range(len(self.card_ranks)):
                if self.card_ranks[i] != other.card_ranks[i]:
                    return False
            return True
        return False


def best_hand_from_cards(cards: List[Card]) -> Hand:
    """Return the best 5-card Hand from an arbitrary list of Card objects."""
    all_cards = sorted(cards)
    if len(all_cards) < 5:
        return Hand(all_cards, sorted=True)
    best = None
    for combo in itertools.combinations(all_cards, 5):
        hand = Hand(list(combo), sorted=True)
        if best is None or hand > best:
            best = hand
    return best
