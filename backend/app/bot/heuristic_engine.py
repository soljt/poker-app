"""
Heuristic poker decision engine.

Scores each decision as a weighted combination of:
  - current made-hand strength  (normalised hand rank 0-1)
  - potential to improve        (expected improvement over remaining deck)

All weights are constructor parameters so they can be tuned without touching
implementation logic.
"""

from app.bot.decision_engine import DecisionEngine
from app.game_logic.game_logic import Card, best_hand_from_cards

DEFAULT_PHASE_ALPHA = {"flop": 0.4, "turn": 0.7, "river": 1.0}


class HeuristicDecisionEngine(DecisionEngine):
    """
    Parameters
    ----------
    aggr_thresh : float
        Score threshold above which the bot plays aggressively (raise/bet).
        Default 0.55.
    call_thresh : float
        Score threshold above which the bot calls/checks rather than folding.
        Default 0.35.
    raise_fraction : float
        Fraction of the bot's stack used as the target raise size at maximum
        aggression (score=1.0). Actual raise scales linearly between min_raise
        and this target. Default 0.25 (25% of stack).
    phase_alpha : dict | None
        Maps phase name → weight given to current made-hand strength vs.
        potential. E.g. {"flop": 0.4, "turn": 0.7, "river": 1.0}.
        Omit to use the defaults.
    preflop_pair_bonus : float
        Added to base preflop score for a pocket pair. Default 0.30.
    preflop_suited_bonus : float
        Added to base preflop score when hole cards share a suit. Default 0.05.
    preflop_connected_bonus : float
        Added to base preflop score when hole card rank gap is 1 or 2.
        Default 0.05.
    """

    def __init__(
        self,
        aggr_thresh: float = 0.30,
        call_thresh: float = 0.05,
        raise_fraction: float = 0.25,
        phase_alpha: dict | None = None,
        preflop_pair_bonus: float = 0.30,
        preflop_suited_bonus: float = 0.05,
        preflop_connected_bonus: float = 0.05,
    ):
        self.aggr_thresh = aggr_thresh
        self.call_thresh = call_thresh
        self.raise_fraction = raise_fraction
        self.phase_alpha = phase_alpha if phase_alpha is not None else dict(DEFAULT_PHASE_ALPHA)
        self.preflop_pair_bonus = preflop_pair_bonus
        self.preflop_suited_bonus = preflop_suited_bonus
        self.preflop_connected_bonus = preflop_connected_bonus

    # ── public interface ────────────────────────────────────────────────────

    def decide(self, game_state: dict, available_actions: list[dict]) -> tuple[str, int | None]:
        score = self._compute_score(game_state)
        return self._choose_action(score, available_actions, game_state)

    # ── scoring ─────────────────────────────────────────────────────────────

    def _compute_score(self, game_state: dict) -> float:
        phase = game_state["phase"]
        hole_cards = [_parse_card(s) for s in game_state["my_cards"]]
        board_cards = [_parse_card(s) for s in game_state["board"]]

        if phase == "preflop":
            return _preflop_strength(
                hole_cards,
                self.preflop_pair_bonus,
                self.preflop_suited_bonus,
                self.preflop_connected_bonus,
            )

        current_norm = _current_strength(hole_cards, board_cards)
        alpha = self.phase_alpha.get(phase, 1.0)

        if alpha >= 1.0:
            return current_norm

        potential = _potential(hole_cards, board_cards, current_norm)
        return alpha * current_norm + (1.0 - alpha) * potential

    # ── action selection ────────────────────────────────────────────────────

    def _choose_action(
        self, score: float, available_actions: list[dict], game_state: dict
    ) -> tuple[str, int | None]:
        actions_by_name = {a["action"]: a for a in available_actions}

        if score >= self.aggr_thresh:
            for name in ("raise", "reraise", "bet", "call", "check"):
                if name in actions_by_name:
                    a = actions_by_name[name]
                    amount = a.get("min")
                    if name in ("raise", "reraise", "bet") and amount is not None:
                        raise_factor = (score - self.aggr_thresh) / (1.0 - self.aggr_thresh)
                        my_chips = game_state.get("my_chips", 0)
                        target = amount + raise_factor * (my_chips * self.raise_fraction - amount)
                        amount = max(amount, int(target))
                    return name, amount

        if score >= self.call_thresh:
            for name in ("check", "call"):
                if name in actions_by_name:
                    return name, None

        # passive: take free card or fold
        if "check" in actions_by_name:
            return "check", None
        if "fold" in actions_by_name:
            return "fold", None

        # last resort fallback
        a = available_actions[0]
        return a["action"], a.get("min")


# ── module-level pure helpers (importable for unit tests) ──────────────────

def _parse_card(card_str: str) -> Card:
    rank, _, suit = card_str.partition(" of ")
    return Card(rank, suit)


def _preflop_strength(
    hole_cards: list,
    pair_bonus: float,
    suited_bonus: float,
    connected_bonus: float,
) -> float:
    """Hole-card quality heuristic for the preflop phase (0–1)."""
    ranks = sorted([Card.RANKS.index(c.rank) for c in hole_cards], reverse=True)
    base = (ranks[0] + ranks[1]) / 24.0  # max = Ace(12) + Ace(12) = 24
    if ranks[0] == ranks[1]:
        base += pair_bonus
    if hole_cards[0].suit == hole_cards[1].suit:
        base += suited_bonus
    if 1 <= abs(ranks[0] - ranks[1]) <= 2:
        base += connected_bonus
    return min(base, 1.0)


def _current_strength(hole_cards: list, board_cards: list) -> float:
    """Best made-hand rank, normalised to 0–1."""
    rank = best_hand_from_cards(hole_cards + board_cards).hand_rank
    return (rank - 1) / 9.0


def _potential(
    hole_cards: list, board_cards: list, current_norm: float
) -> float:
    """Expected improvement in normalised strength from the next unknown card."""
    known_reprs = {repr(c) for c in hole_cards + board_cards}
    remaining = [
        Card(r, s)
        for r in Card.RANKS
        for s in Card.SUITS
        if repr(Card(r, s)) not in known_reprs
    ]
    if not remaining:
        return 0.0
    future_norms = [
        (_current_strength(hole_cards, board_cards + [c]))
        for c in remaining
    ]
    avg_future = sum(future_norms) / len(future_norms)
    return max(0.0, avg_future - current_norm)
