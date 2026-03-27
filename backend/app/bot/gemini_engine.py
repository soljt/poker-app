import json
import os
import re

from google import genai
from google.genai import types

from app.bot.decision_engine import DecisionEngine, RandomDecisionEngine

_SYSTEM_PROMPT = """\
You are a poker bot playing Texas Hold'em. Analyse the game state and choose an action.

Respond with ONLY a JSON object — no explanation, no markdown, no extra text:
{"action": "<action>", "amount": <integer_or_null>}

Constraints:
- "action" must be exactly one of the strings listed under "Available actions"
- "amount" must be an integer >= the listed "min" for bet/raise/reraise actions
- "amount" must be null for fold/check/call actions
"""


def _build_prompt(game_state: dict, available_actions: list[dict]) -> str:
    board = game_state.get("board") or []
    my_cards = game_state.get("my_cards") or []
    phase = game_state.get("phase", "unknown")
    pots = game_state.get("pots") or []
    players = game_state.get("players") or []
    my_chips = game_state.get("my_chips", 0)
    my_bet = game_state.get("my_bet", 0)
    table_bet = game_state.get("table_bet", 0)
    blinds = game_state.get("blinds", [0, 0])

    total_pot = sum(p["amount"] for p in pots)

    players_str = "\n".join(
        f"  {p['username']}: {p['chips']} chips behind, "
        f"bet {p['current_bet']} this round"
        f"{', FOLDED' if p['folded'] else ''}"
        for p in players
    )

    actions_str = "\n".join(
        f"  {a['action']}"
        + (f" (min amount: {a['min']})" if a.get("min") is not None else "")
        + (" [all-in]" if a.get("allin") else "")
        for a in available_actions
    )

    return f"""\
Phase: {phase}
Blinds: {blinds[0]}/{blinds[1]}
Your hole cards: {', '.join(my_cards) or '(none)'}
Board: {', '.join(board) or '(none yet)'}
Total pot: {total_pot}
Your chips: {my_chips}  |  Your current bet: {my_bet}  |  Table bet: {table_bet}

Players at the table:
{players_str}

Available actions:
{actions_str}

Choose your action:"""


def _parse_response(response_text: str, available_actions: list[dict]) -> tuple[str, int | None]:
    """Parse and validate an LLM response string into (action, amount)."""
    # strip markdown code fences if the model wrapped its output
    cleaned = re.sub(r"```(?:json)?", "", response_text).strip()
    data = json.loads(cleaned)

    action = data.get("action")
    amount = data.get("amount")

    valid = {a["action"]: a for a in available_actions}
    if action not in valid:
        raise ValueError(f"Unknown action '{action}'; valid: {list(valid)}")

    action_info = valid[action]
    min_amount = action_info.get("min")

    if min_amount is not None:
        # action requires an amount
        if amount is None:
            amount = min_amount          # be generous: default to minimum
        elif amount < min_amount:
            raise ValueError(
                f"Amount {amount} is below minimum {min_amount} for '{action}'"
            )
        amount = int(amount)
    else:
        amount = None

    return action, amount


class GeminiDecisionEngine(DecisionEngine):
    """Queries the Gemini API to pick a poker action. Falls back to a RandomDecisionEngine on error."""

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        fallback: DecisionEngine | None = None,
    ):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.config = types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT)
        self.fallback = fallback if fallback is not None else RandomDecisionEngine()

    def decide(self, game_state: dict, available_actions: list[dict]) -> tuple[str, int | None]:
        try:
            prompt = _build_prompt(game_state, available_actions)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config,
            )
            return _parse_response(response.text, available_actions)
        except Exception as e:
            print(
                f"[GeminiDecisionEngine] falling back to "
                f"{self.fallback.__class__.__name__}: {e}"
            )
            return self.fallback.decide(game_state, available_actions)
