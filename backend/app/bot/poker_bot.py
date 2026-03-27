from app.bot.decision_engine import DecisionEngine
from app.game_logic.game_logic import PokerRound


class PokerBot:
    """
    Wraps a DecisionEngine and a username to act as a player in a PokerRound.

    The engine is the only thing that needs to change to swap in a different
    strategy (heuristic, RL agent, etc.) — the bot itself is engine-agnostic.
    """

    def __init__(self, username: str, engine: DecisionEngine):
        self.username = username
        self.engine = engine

    def get_action(self, game: PokerRound) -> tuple[str, int | None]:
        """
        Serialize the game state for this bot's perspective and ask the engine
        for an action.

        Returns:
            (action, amount) ready to pass to game.handle_player_action()
        """
        game_state = game.serialize_for_player(self.username)
        available_actions = game_state.get("available_actions") or []
        return self.engine.decide(game_state, available_actions)
