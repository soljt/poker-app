from enum import StrEnum, IntEnum


class Rank(StrEnum):
    TWO   = "2"
    THREE = "3"
    FOUR  = "4"
    FIVE  = "5"
    SIX   = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE  = "9"
    TEN   = "10"
    JACK  = "J"
    QUEEN = "Q"
    KING  = "K"
    ACE   = "A"


class Suit(StrEnum):
    CLUBS    = "clubs"
    SPADES   = "spades"
    HEARTS   = "hearts"
    DIAMONDS = "diamonds"


class Action(StrEnum):
    CHECK   = "check"
    RAISE   = "raise"
    BET     = "bet"
    RERAISE = "reraise"
    CALL    = "call"
    FOLD    = "fold"


class Phase(StrEnum):
    PREFLOP = "preflop"
    FLOP    = "flop"
    TURN    = "turn"
    RIVER   = "river"


class HandRank(IntEnum):
    HIGH_CARD      = 1
    PAIR           = 2
    TWO_PAIR       = 3
    TRIPS          = 4
    STRAIGHT       = 5
    FLUSH          = 6
    FULL_HOUSE     = 7
    QUADS          = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH    = 10

    @property
    def label(self) -> str:
        return self.name.replace("_", " ").title()
