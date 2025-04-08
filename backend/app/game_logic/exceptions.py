class PokerValidationError(Exception):
    """Base exception for validation-related issues."""
    pass

class InvalidActionError(PokerValidationError):
    def __init__(self, action, reason="Invalid or unavailable action."):
        super().__init__(f"Invalid action '{action}': {reason}")
        self.action = action
        self.reason = reason

class InvalidAmountError(PokerValidationError):
    def __init__(self, amount, reason="Invalid amount for this action."):
        super().__init__(f"Invalid amount '{amount}': {reason}")
        self.amount = amount
        self.reason = reason

class NotPlayersTurnError(PokerValidationError):
    def __init__(self, player):
        super().__init__(f"It is not {player.name}'s turn.")
        self.player = player