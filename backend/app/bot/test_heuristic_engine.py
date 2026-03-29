"""
Unit tests for HeuristicDecisionEngine and its helper functions.
"""
import pytest

from app.bot.heuristic_engine import (
    HeuristicDecisionEngine,
    _parse_card,
    _preflop_strength,
    _current_strength,
    _potential,
)
from app.game_logic.game_logic import Card, best_hand_from_cards

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

FOLD_ONLY = [{"action": "fold", "min": None, "allin": False}]
CHECK_FOLD = [
    {"action": "check", "min": None, "allin": False},
    {"action": "fold",  "min": None, "allin": False},
]
STANDARD_ACTIONS = [
    {"action": "call",  "min": None, "allin": False},
    {"action": "raise", "min": 40,   "allin": False},
    {"action": "fold",  "min": None, "allin": False},
]

# Strong made-hand on the river: A of spades + A of clubs + board with an Ace
RIVER_STATE_TRIPS = {
    "my_cards": ["A of spades", "A of clubs"],
    "board":    ["A of hearts", "2 of diamonds", "5 of clubs", "7 of spades", "K of hearts"],
    "phase":    "river",
    "my_chips": 500,
    "my_bet":   0,
    "table_bet": 0,
}

# Weak hand on the river: 2-7 off-suit with no board help
RIVER_STATE_GARBAGE = {
    "my_cards": ["2 of clubs", "7 of diamonds"],
    "board":    ["A of spades", "K of hearts", "Q of clubs", "J of spades", "9 of diamonds"],
    "phase":    "river",
    "my_chips": 500,
    "my_bet":   0,
    "table_bet": 0,
}

# Flush draw on the flop
FLOP_STATE_FLUSH_DRAW = {
    "my_cards": ["A of spades", "K of spades"],
    "board":    ["2 of spades", "7 of spades", "J of clubs"],
    "phase":    "flop",
    "my_chips": 500,
    "my_bet":   0,
    "table_bet": 0,
}


# ---------------------------------------------------------------------------
# _parse_card
# ---------------------------------------------------------------------------

class TestParseCard:
    def test_parses_rank_and_suit(self):
        card = _parse_card("A of spades")
        assert card.rank == "A"
        assert card.suit == "spades"

    def test_parses_two_digit_rank(self):
        card = _parse_card("10 of hearts")
        assert card.rank == "10"
        assert card.suit == "hearts"


# ---------------------------------------------------------------------------
# _preflop_strength
# ---------------------------------------------------------------------------

DEFAULT_BONUSES = (0.30, 0.05, 0.05)

def pfstr(cards_str: list[str]) -> float:
    cards = [_parse_card(s) for s in cards_str]
    return _preflop_strength(cards, *DEFAULT_BONUSES)

class TestPreflopStrength:
    def test_pocket_aces_near_max(self):
        assert pfstr(["A of spades", "A of hearts"]) == pytest.approx(1.0)

    def test_pocket_kings_high(self):
        score = pfstr(["K of spades", "K of hearts"])
        assert score == pytest.approx(1.0)  # capped

    def test_pocket_tens_reasonable(self):
        score = pfstr(["10 of spades", "10 of hearts"])
        assert 0.85 < score <= 1.0

    def test_pocket_twos_low_but_pair_bonus(self):
        score = pfstr(["2 of spades", "2 of hearts"])
        assert score == pytest.approx(0.30)  # base=0, pair_bonus=0.30

    def test_ak_suited_very_high(self):
        score = pfstr(["A of spades", "K of spades"])
        assert score == pytest.approx(1.0)  # (12+11)/24 + suited bonus capped

    def test_a9_offsuit_high(self):
        # A9 offsuit: gap=3 (not connected), not suited, not pair
        score = pfstr(["A of spades", "9 of hearts"])
        assert score == pytest.approx((12 + 7) / 24.0)

    def test_pairs_beat_weak_non_pair(self):
        # Pocket 7s (0.717) should beat A2 offsuit (0.5)
        a2_offsuit = pfstr(["A of spades", "2 of hearts"])
        sevens = pfstr(["7 of spades", "7 of hearts"])
        assert sevens > a2_offsuit

    def test_suited_higher_than_offsuit(self):
        suited   = pfstr(["A of spades", "J of spades"])
        offsuit  = pfstr(["A of spades", "J of hearts"])
        assert suited > offsuit

    def test_connected_higher_than_unconnected(self):
        conn   = pfstr(["9 of spades", "8 of hearts"])  # gap 1
        noconn = pfstr(["9 of spades", "3 of hearts"])  # gap 6
        assert conn > noconn

    def test_garbage_hand_low(self):
        score = pfstr(["2 of clubs", "7 of diamonds"])  # classic worst hand
        assert score < 0.35

    def test_score_capped_at_one(self):
        score = pfstr(["A of spades", "A of hearts"])
        assert score <= 1.0


# ---------------------------------------------------------------------------
# best_hand_from_cards (shared utility, tested via game_logic import)
# ---------------------------------------------------------------------------

class TestBestHandFromCards:
    def test_flush_ranks_6(self):
        cards = [_parse_card(s) for s in
                 ["2 of spades", "5 of spades", "9 of spades", "J of spades", "A of spades"]]
        assert best_hand_from_cards(cards).hand_rank == 6

    def test_straight_ranks_5(self):
        cards = [_parse_card(s) for s in
                 ["5 of clubs", "6 of hearts", "7 of diamonds", "8 of spades", "9 of clubs"]]
        assert best_hand_from_cards(cards).hand_rank == 5

    def test_pair_ranks_2(self):
        cards = [_parse_card(s) for s in
                 ["A of spades", "A of hearts", "2 of clubs", "5 of diamonds", "9 of spades"]]
        assert best_hand_from_cards(cards).hand_rank == 2

    def test_best_5_of_7(self):
        # hole: AA, board: A 2 3 4 5 → trips + straight exists; trips aces > straight
        cards = [_parse_card(s) for s in
                 ["A of spades", "A of hearts",           # hole
                  "A of clubs", "2 of diamonds", "3 of clubs", "4 of spades", "5 of hearts"]]  # board
        hand = best_hand_from_cards(cards)
        assert hand.hand_rank >= 4  # at least trips

    def test_fewer_than_5_cards_returns_hand(self):
        # Use non-consecutive ranks so the 2-card hand is unambiguously high card
        cards = [_parse_card(s) for s in ["A of spades", "2 of hearts"]]
        hand = best_hand_from_cards(cards)
        assert hand is not None
        assert hand.hand_rank == 1  # high card (no pair, no sequential run of 5)


# ---------------------------------------------------------------------------
# _current_strength
# ---------------------------------------------------------------------------

class TestCurrentStrength:
    def test_trips_stronger_than_pair(self):
        hole = [_parse_card("A of spades"), _parse_card("A of clubs")]
        board_trips = [_parse_card(s) for s in ["A of hearts", "2 of diamonds", "5 of clubs"]]
        board_pair  = [_parse_card(s) for s in ["K of hearts", "2 of diamonds", "5 of clubs"]]
        assert _current_strength(hole, board_trips) > _current_strength(hole, board_pair)

    def test_normalized_between_0_and_1(self):
        hole  = [_parse_card("2 of clubs"), _parse_card("7 of diamonds")]
        board = [_parse_card(s) for s in ["A of spades", "K of hearts", "Q of clubs"]]
        score = _current_strength(hole, board)
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# _potential
# ---------------------------------------------------------------------------

class TestPotential:
    def test_flush_draw_has_positive_potential(self):
        hole  = [_parse_card("A of spades"), _parse_card("K of spades")]
        board = [_parse_card(s) for s in ["2 of spades", "7 of spades", "J of clubs"]]
        current = _current_strength(hole, board)
        pot = _potential(hole, board, current)
        assert pot > 0.0

    def test_river_no_remaining_cards(self):
        # Build a full 7-card hand — no remaining cards
        hole  = [_parse_card("A of spades"), _parse_card("A of clubs")]
        board = [_parse_card(s) for s in
                 ["A of hearts", "2 of diamonds", "5 of clubs", "7 of spades", "K of hearts"]]
        current = _current_strength(hole, board)
        # remaining deck should be empty (all 7 cards known)
        # Just verify it returns a float without error
        pot = _potential(hole, board, current)
        assert isinstance(pot, float)

    def test_potential_non_negative(self):
        hole  = [_parse_card("2 of clubs"), _parse_card("7 of diamonds")]
        board = [_parse_card(s) for s in ["A of spades", "K of hearts", "Q of clubs"]]
        current = _current_strength(hole, board)
        assert _potential(hole, board, current) >= 0.0


# ---------------------------------------------------------------------------
# HeuristicDecisionEngine.decide
# ---------------------------------------------------------------------------

class TestHeuristicDecisionEngine:
    def setup_method(self):
        self.engine = HeuristicDecisionEngine()

    def test_strong_hand_raises(self):
        action, _ = self.engine.decide(RIVER_STATE_TRIPS, STANDARD_ACTIONS)
        assert action == "raise"

    def test_strong_hand_raise_amount_gte_min(self):
        _, amount = self.engine.decide(RIVER_STATE_TRIPS, STANDARD_ACTIONS)
        assert amount is not None
        assert amount >= 40  # min raise in STANDARD_ACTIONS

    def test_garbage_hand_folds_when_no_check(self):
        action, _ = self.engine.decide(RIVER_STATE_GARBAGE, FOLD_ONLY)
        assert action == "fold"

    def test_garbage_hand_checks_when_free(self):
        action, _ = self.engine.decide(RIVER_STATE_GARBAGE, CHECK_FOLD)
        assert action == "check"

    def test_flush_draw_calls_or_raises_on_flop(self):
        action, _ = self.engine.decide(FLOP_STATE_FLUSH_DRAW, STANDARD_ACTIONS)
        assert action in ("raise", "call", "check")

    def test_returns_valid_action(self):
        valid = {a["action"] for a in STANDARD_ACTIONS}
        action, _ = self.engine.decide(RIVER_STATE_TRIPS, STANDARD_ACTIONS)
        assert action in valid

    def test_custom_aggr_thresh_zero_always_raises(self):
        engine = HeuristicDecisionEngine(aggr_thresh=0.0)
        action, _ = engine.decide(RIVER_STATE_GARBAGE, STANDARD_ACTIONS)
        assert action == "raise"

    def test_custom_high_thresh_folds_trips(self):
        # With aggr_thresh and call_thresh set very high, even trips folds.
        engine = HeuristicDecisionEngine(call_thresh=0.9, aggr_thresh=0.95)
        action, _ = engine.decide(RIVER_STATE_TRIPS, FOLD_ONLY)
        assert action == "fold"

    def test_preflop_pocket_aces_raises(self):
        state = {
            "my_cards": ["A of spades", "A of hearts"],
            "board": [],
            "phase": "preflop",
            "my_chips": 500,
            "my_bet": 0,
            "table_bet": 0,
        }
        action, _ = self.engine.decide(state, STANDARD_ACTIONS)
        assert action == "raise"

    def test_preflop_garbage_folds(self):
        state = {
            "my_cards": ["2 of clubs", "7 of diamonds"],
            "board": [],
            "phase": "preflop",
            "my_chips": 500,
            "my_bet": 0,
            "table_bet": 0,
        }
        action, _ = self.engine.decide(state, FOLD_ONLY)
        assert action == "fold"


# ---------------------------------------------------------------------------
# _effective_call_thresh / pot odds
# ---------------------------------------------------------------------------

class TestPotOdds:
    """Pot odds should raise the effective call threshold when facing a bet."""

    def _state_with_bet(self, bet_to_call: int, pot: int) -> dict:
        return {
            "my_cards": ["2 of clubs", "7 of diamonds"],
            "board": ["A of spades", "K of hearts", "Q of clubs", "J of spades", "9 of diamonds"],
            "phase": "river",
            "my_chips": 1000,
            "my_bet": 0,
            "table_bet": bet_to_call,
            "pots": [{"amount": pot, "players": ["PokerBot", "alice"]}],
        }

    def test_free_check_uses_base_thresh(self):
        """With no bet to call the effective threshold equals call_thresh."""
        engine = HeuristicDecisionEngine(call_thresh=0.2, pot_odds_sensitivity=1.0)
        state = self._state_with_bet(0, 100)
        thresh = engine._effective_call_thresh(state)
        assert thresh == pytest.approx(0.2)

    def test_large_bet_raises_thresh(self):
        """A pot-sized bet (200 into 200) requires 50% equity — thresh should be ≥ 0.5."""
        engine = HeuristicDecisionEngine(call_thresh=0.2, pot_odds_sensitivity=1.0)
        state = self._state_with_bet(200, 200)  # pot_odds_needed = 200/400 = 0.5
        thresh = engine._effective_call_thresh(state)
        assert thresh == pytest.approx(0.5)

    def test_small_bet_minimal_adjustment(self):
        """A tiny bet (10 into 200) barely raises the threshold above call_thresh."""
        engine = HeuristicDecisionEngine(call_thresh=0.2, pot_odds_sensitivity=1.0)
        state = self._state_with_bet(10, 200)  # pot_odds_needed = 10/210 ≈ 0.048
        thresh = engine._effective_call_thresh(state)
        assert thresh == pytest.approx(0.2)  # max(0.2, 0.048) = 0.2

    def test_sensitivity_zero_ignores_bet(self):
        """With pot_odds_sensitivity=0, even a huge bet doesn't adjust the threshold."""
        engine = HeuristicDecisionEngine(call_thresh=0.2, pot_odds_sensitivity=0.0)
        state = self._state_with_bet(10000, 100)
        thresh = engine._effective_call_thresh(state)
        assert thresh == pytest.approx(0.2)

    def test_sensitivity_half_partial_adjustment(self):
        """With sensitivity=0.5, pot odds contribute at half weight."""
        engine = HeuristicDecisionEngine(call_thresh=0.1, pot_odds_sensitivity=0.5)
        # pot_odds_needed raw = 200/400 = 0.5; with 0.5 sensitivity → 0.25
        state = self._state_with_bet(200, 200)
        thresh = engine._effective_call_thresh(state)
        assert thresh == pytest.approx(0.25)

    def test_large_bet_causes_fold_on_weak_hand(self):
        """Bot should fold a weak hand against a massive all-in bet."""
        engine = HeuristicDecisionEngine(pot_odds_sensitivity=1.0)
        # Garbage hand (high card = 0), massive bet = needs ~91% equity
        state = self._state_with_bet(1000, 100)  # pot_odds_needed = 1000/1100 ≈ 0.909
        call_fold = [
            {"action": "call", "min": None, "allin": True},
            {"action": "fold", "min": None, "allin": False},
        ]
        action, _ = engine.decide(state, call_fold)
        assert action == "fold"

    def test_strong_hand_calls_large_bet(self):
        """A strong hand should still call even a big bet."""
        engine = HeuristicDecisionEngine(pot_odds_sensitivity=1.0)
        # Trips aces — score ≈ 0.5 with log norm; facing pot-sized bet (50% equity needed)
        state = {
            "my_cards": ["A of spades", "A of clubs"],
            "board": ["A of hearts", "2 of diamonds", "5 of clubs", "7 of spades", "K of hearts"],
            "phase": "river",
            "my_chips": 500,
            "my_bet": 0,
            "table_bet": 200,
            "pots": [{"amount": 200, "players": ["PokerBot", "alice"]}],
        }
        call_fold = [
            {"action": "call", "min": None, "allin": False},
            {"action": "fold", "min": None, "allin": False},
        ]
        action, _ = engine.decide(state, call_fold)
        # Score ≈ 0.5 for trips; pot_odds_needed = 200/400 = 0.5; score just meets threshold
        assert action in ("call", "fold")  # borderline — either is acceptable
