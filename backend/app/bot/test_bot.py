"""
Unit tests for the poker bot module.

Covers:
  - RandomDecisionEngine: always returns a valid (action, amount) pair
  - _build_prompt: correct game state fields appear in the output
  - _parse_response: valid/invalid JSON, unknown actions, amount validation
  - GeminiDecisionEngine: API call path and fallback behaviour (model mocked)
  - PokerBot: delegates to the engine with the correct game state
"""
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from app.bot.decision_engine import RandomDecisionEngine
from app.bot.gemini_engine import GeminiDecisionEngine, _build_prompt, _parse_response


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

FOLD_ONLY = [{"action": "fold", "min": None, "allin": False}]

STANDARD_ACTIONS = [
    {"action": "call",  "min": None, "allin": False},
    {"action": "raise", "min": 40,   "allin": False},
    {"action": "fold",  "min": None, "allin": False},
]

MINIMAL_GAME_STATE = {
    "my_cards":  ["A of spades", "K of hearts"],
    "board":     ["2 of clubs", "7 of diamonds", "J of spades"],
    "players": [
        {"username": "bot",  "chips": 980, "folded": False, "current_bet": 20},
        {"username": "hero", "chips": 960, "folded": False, "current_bet": 40},
    ],
    "pots":      [{"amount": 60, "players": ["bot", "hero"]}],
    "blinds":    [10, 20],
    "my_chips":  980,
    "my_bet":    20,
    "table_bet": 40,
    "phase":     "flop",
}


# ---------------------------------------------------------------------------
# RandomDecisionEngine
# ---------------------------------------------------------------------------

class TestRandomDecisionEngine:
    def setup_method(self):
        self.engine = RandomDecisionEngine()

    def test_returns_valid_action(self):
        action, _ = self.engine.decide(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        valid = {a["action"] for a in STANDARD_ACTIONS}
        assert action in valid

    def test_returns_none_amount_for_fold(self):
        # force fold by limiting available actions
        action, amount = self.engine.decide(MINIMAL_GAME_STATE, FOLD_ONLY)
        assert action == "fold"
        assert amount is None

    def test_returns_min_amount_for_raise(self):
        raise_only = [{"action": "raise", "min": 80, "allin": False}]
        action, amount = self.engine.decide(MINIMAL_GAME_STATE, raise_only)
        assert action == "raise"
        assert amount == 80

    def test_returns_none_amount_for_call(self):
        call_only = [{"action": "call", "min": None, "allin": False}]
        _, amount = self.engine.decide(MINIMAL_GAME_STATE, call_only)
        assert amount is None

    def test_works_with_multiple_actions(self):
        # Run many times; every result must be valid
        valid = {a["action"] for a in STANDARD_ACTIONS}
        for _ in range(50):
            action, _ = self.engine.decide(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
            assert action in valid


# ---------------------------------------------------------------------------
# _build_prompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def test_contains_hole_cards(self):
        prompt = _build_prompt(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert "A of spades" in prompt
        assert "K of hearts" in prompt

    def test_contains_board_cards(self):
        prompt = _build_prompt(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert "2 of clubs" in prompt
        assert "J of spades" in prompt

    def test_contains_phase(self):
        prompt = _build_prompt(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert "flop" in prompt

    def test_contains_pot_total(self):
        prompt = _build_prompt(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert "60" in prompt

    def test_contains_available_action_names(self):
        prompt = _build_prompt(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert "call" in prompt
        assert "raise" in prompt
        assert "fold" in prompt

    def test_contains_raise_minimum(self):
        prompt = _build_prompt(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert "40" in prompt  # raise min

    def test_empty_board_shows_none(self):
        state = {**MINIMAL_GAME_STATE, "board": []}
        prompt = _build_prompt(state, FOLD_ONLY)
        assert "none" in prompt.lower()

    def test_contains_player_usernames(self):
        prompt = _build_prompt(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert "bot" in prompt
        assert "hero" in prompt

    def test_contains_blinds(self):
        prompt = _build_prompt(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert "10" in prompt
        assert "20" in prompt


# ---------------------------------------------------------------------------
# _parse_response
# ---------------------------------------------------------------------------

class TestParseResponse:
    def test_valid_fold(self):
        raw = json.dumps({"action": "fold", "amount": None})
        action, amount = _parse_response(raw, STANDARD_ACTIONS)
        assert action == "fold"
        assert amount is None

    def test_valid_call(self):
        raw = json.dumps({"action": "call", "amount": None})
        action, amount = _parse_response(raw, STANDARD_ACTIONS)
        assert action == "call"
        assert amount is None

    def test_valid_raise_with_amount(self):
        raw = json.dumps({"action": "raise", "amount": 100})
        action, amount = _parse_response(raw, STANDARD_ACTIONS)
        assert action == "raise"
        assert amount == 100

    def test_raise_defaults_to_min_when_amount_null(self):
        raw = json.dumps({"action": "raise", "amount": None})
        action, amount = _parse_response(raw, STANDARD_ACTIONS)
        assert action == "raise"
        assert amount == 40  # falls back to "min" from STANDARD_ACTIONS

    def test_raises_on_amount_below_min(self):
        raw = json.dumps({"action": "raise", "amount": 10})
        with pytest.raises(ValueError, match="below minimum"):
            _parse_response(raw, STANDARD_ACTIONS)

    def test_raises_on_unknown_action(self):
        raw = json.dumps({"action": "shove", "amount": None})
        with pytest.raises(ValueError, match="Unknown action"):
            _parse_response(raw, STANDARD_ACTIONS)

    def test_raises_on_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_response("not json at all", STANDARD_ACTIONS)

    def test_strips_markdown_fences(self):
        raw = "```json\n" + json.dumps({"action": "fold", "amount": None}) + "\n```"
        action, amount = _parse_response(raw, STANDARD_ACTIONS)
        assert action == "fold"

    def test_amount_cast_to_int(self):
        # Model might return a float
        raw = json.dumps({"action": "raise", "amount": 80.0})
        _, amount = _parse_response(raw, STANDARD_ACTIONS)
        assert isinstance(amount, int)
        assert amount == 80

    def test_null_amount_for_call_is_preserved(self):
        raw = json.dumps({"action": "call", "amount": None})
        _, amount = _parse_response(raw, STANDARD_ACTIONS)
        assert amount is None


# ---------------------------------------------------------------------------
# GeminiDecisionEngine
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_genai(monkeypatch):
    """Patch genai.Client so no real API calls are made."""
    mock_module = MagicMock()
    monkeypatch.setattr("app.bot.gemini_engine.genai", mock_module)
    return mock_module


def _set_response(mock_genai, response_text: str):
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_genai.Client.return_value.models.generate_content.return_value = mock_response


class TestGeminiDecisionEngine:
    def _make_engine(self, mock_genai, response_text: str) -> GeminiDecisionEngine:
        _set_response(mock_genai, response_text)
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            engine = GeminiDecisionEngine()
        return engine

    def test_calls_model_and_returns_parsed_action(self, mock_genai):
        engine = self._make_engine(mock_genai, json.dumps({"action": "fold", "amount": None}))
        action, amount = engine.decide(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert action == "fold"
        assert amount is None
        mock_genai.Client.return_value.models.generate_content.assert_called_once()

    def test_returns_raise_with_amount(self, mock_genai):
        engine = self._make_engine(mock_genai, json.dumps({"action": "raise", "amount": 60}))
        action, amount = engine.decide(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert action == "raise"
        assert amount == 60

    def test_falls_back_on_api_error(self, mock_genai):
        mock_genai.Client.return_value.models.generate_content.side_effect = RuntimeError("API down")
        fallback = MagicMock(spec=RandomDecisionEngine)
        fallback.decide.return_value = ("fold", None)

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            engine = GeminiDecisionEngine(fallback=fallback)

        action, amount = engine.decide(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        fallback.decide.assert_called_once_with(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        assert action == "fold"

    def test_falls_back_on_parse_error(self, mock_genai):
        engine = self._make_engine(mock_genai, "I cannot decide right now")
        fallback = MagicMock(spec=RandomDecisionEngine)
        fallback.decide.return_value = ("call", None)
        engine.fallback = fallback

        action, _ = engine.decide(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        fallback.decide.assert_called_once()
        assert action == "call"

    def test_falls_back_on_invalid_action_in_response(self, mock_genai):
        engine = self._make_engine(mock_genai, json.dumps({"action": "shove", "amount": None}))
        fallback = MagicMock(spec=RandomDecisionEngine)
        fallback.decide.return_value = ("fold", None)
        engine.fallback = fallback

        engine.decide(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        fallback.decide.assert_called_once()

    def test_raises_without_api_key(self, mock_genai):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GEMINI_API_KEY", None)
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                GeminiDecisionEngine()

    def test_default_fallback_is_random_engine(self, mock_genai):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            engine = GeminiDecisionEngine()
        assert isinstance(engine.fallback, RandomDecisionEngine)

    def test_prompt_passed_to_model(self, mock_genai):
        engine = self._make_engine(mock_genai, json.dumps({"action": "fold", "amount": None}))
        engine.decide(MINIMAL_GAME_STATE, STANDARD_ACTIONS)
        call_kwargs = mock_genai.Client.return_value.models.generate_content.call_args[1]
        prompt_arg = call_kwargs["contents"]
        assert "A of spades" in prompt_arg
        assert "flop" in prompt_arg


# ---------------------------------------------------------------------------
# PokerBot
# ---------------------------------------------------------------------------

class TestPokerBot:
    def _make_mock_game(self):
        game = MagicMock()
        game.serialize_for_player.return_value = {
            **MINIMAL_GAME_STATE,
            "available_actions": STANDARD_ACTIONS,
        }
        return game

    def test_get_action_delegates_to_engine(self):
        from app.bot.poker_bot import PokerBot

        engine = MagicMock(spec=RandomDecisionEngine)
        engine.decide.return_value = ("call", None)
        bot = PokerBot("bot", engine)
        game = self._make_mock_game()

        action, amount = bot.get_action(game)

        engine.decide.assert_called_once()
        assert action == "call"
        assert amount is None

    def test_get_action_serializes_for_correct_username(self):
        from app.bot.poker_bot import PokerBot

        engine = MagicMock(spec=RandomDecisionEngine)
        engine.decide.return_value = ("fold", None)
        bot = PokerBot("mybot", engine)
        game = self._make_mock_game()

        bot.get_action(game)

        game.serialize_for_player.assert_called_once_with("mybot")

    def test_get_action_passes_available_actions_to_engine(self):
        from app.bot.poker_bot import PokerBot

        engine = MagicMock(spec=RandomDecisionEngine)
        engine.decide.return_value = ("raise", 80)
        bot = PokerBot("bot", engine)
        game = self._make_mock_game()

        bot.get_action(game)

        _, kwargs = engine.decide.call_args
        # decide is called positionally
        called_actions = engine.decide.call_args[0][1]
        assert called_actions == STANDARD_ACTIONS
