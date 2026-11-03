class RavenException(Exception):
    """Base exception for all Ravens engine errors."""
    pass


class RavenStrikeException(RavenException):
    """
    Raised when an agent refuses to process an interaction due to
    exhausted patience (patience < threshold_strike).
    """
    def __init__(self, user_id: str, patience: float, message: str = ""):
        self.user_id = user_id
        self.patience = patience
        body = message.strip() if message else "Repeated hostility or boundary breach."
        full_message = f"[RavenStrike: user='{user_id}', patience={patience:.1f}/100.0] {body}"
        super().__init__(full_message)
