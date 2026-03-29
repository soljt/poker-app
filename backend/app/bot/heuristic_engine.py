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
import math

DEFAULT_PHASE_ALPHA = {"flop": 0.4, "turn": 0.7, "river": 1.0}


class HeuristicDecisionEngine(DecisionEngine):
    """
    Parameters
    ----------
    aggr_thresh : float
        Score threshold above which the bot plays aggressively (raise/bet).
        Default 0.4.
    call_thresh : float
        Score threshold above which the bot calls/checks rather than folding.
        Default 0.2.
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
    pot_odds_sensitivity : float
        Controls how much the size of the bet faced raises the call threshold.
        At 1.0 (default) the effective call threshold equals max(call_thresh,
        pot_odds_needed), where pot_odds_needed = bet_to_call / (pot +
        bet_to_call). At 0.0 pot odds are ignored entirely.
    """

    def __init__(
        self,
        aggr_thresh: float = 0.4,
        call_thresh: float = 0.1,
        raise_fraction: float = 0.25,
        phase_alpha: dict | None = None,
        preflop_pair_bonus: float = 0.30,
        preflop_suited_bonus: float = 0.05,
        preflop_connected_bonus: float = 0.05,
        pot_odds_sensitivity: float = 1.0,
    ):
        self.aggr_thresh = aggr_thresh
        self.call_thresh = call_thresh
        self.raise_fraction = raise_fraction
        self.phase_alpha = phase_alpha if phase_alpha is not None else dict(DEFAULT_PHASE_ALPHA)
        self.preflop_pair_bonus = preflop_pair_bonus
        self.preflop_suited_bonus = preflop_suited_bonus
        self.preflop_connected_bonus = preflop_connected_bonus
        self.pot_odds_sensitivity = pot_odds_sensitivity

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
        effective_call_thresh = self._effective_call_thresh(game_state)

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

        if score >= effective_call_thresh:
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

    def _effective_call_thresh(self, game_state: dict) -> float:
        """Raise the call threshold proportionally to pot odds when facing a bet.

        pot_odds_needed = bet_to_call / (total_pot + bet_to_call)
        effective_thresh = max(call_thresh, pot_odds_needed * pot_odds_sensitivity)
        """
        table_bet = game_state.get("table_bet", 0)
        my_bet = game_state.get("my_bet", 0)
        bet_to_call = max(0, table_bet - my_bet)

        if bet_to_call == 0 or self.pot_odds_sensitivity == 0:
            return self.call_thresh

        total_pot = sum(p["amount"] for p in game_state.get("pots", []))
        denominator = total_pot + bet_to_call
        if denominator == 0:
            return self.call_thresh

        pot_odds_needed = (bet_to_call / denominator) * self.pot_odds_sensitivity
        return max(self.call_thresh, pot_odds_needed)


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


def _current_strength(hole_cards: list, board_cards: list, base: float = 4.0) -> float:
    """Best made-hand rank, normalised to 0–1.
    base controls curvature — higher = bigger jump off rank 1.
    """
    rank = best_hand_from_cards(hole_cards + board_cards).hand_rank
    x = (rank - 1) / 9.0                           # linear 0–1
    return math.log(1 + x * (base - 1)) / math.log(base)  # logarithmic 0–1


def _potential(
    hole_cards: list, board_cards: list, current_norm: float,
    ceiling_weight: float = 0.5
) -> float:
    """Expected improvement in normalised strength from the next unknown card.
    
    ceiling_weight blends avg future strength with max future strength,
    so draws with a high ceiling (e.g. flush draw) aren't diluted by the
    majority of cards that don't hit.
    """
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
        _current_strength(hole_cards, board_cards + [c])
        for c in remaining
    ]
    avg_future = sum(future_norms) / len(future_norms)
    max_future = max(future_norms)
    blended = (1 - ceiling_weight) * avg_future + ceiling_weight * max_future
    return max(0.0, blended - current_norm)
