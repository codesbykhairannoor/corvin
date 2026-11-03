from enum import Enum

class Standing(str, Enum):
    """
    Represents the moral/social standing of a conversational participant in the
    Contrite Tit-for-Tat (CTFT) model (Nowak & Sigmund, 1992; Sugden, 1986).
    """
    GOOD = "GOOD"
    BAD = "BAD"


class StandingEngine:
    """
    Manages standing transitions and contrition resolution based on Nowak & Sigmund (1992).

    Rules:
    - User begins in GOOD standing.
    - If user drops below patience_threshold (defects with an unprovoked toxic prompt),
      user transitions into BAD standing.
    - If user is in BAD standing, the agent retaliates or withholds compliance.
    - When user performs a genuine 'Contrition' (apology or de-escalation prompt),
      standing can be restored to GOOD after restitution / pardon threshold is satisfied.
    """
    def __init__(self, bad_threshold: float = 50.0, pardon_threshold: float = 65.0):
        self.bad_threshold = bad_threshold
        self.pardon_threshold = pardon_threshold

    def evaluate_standing(self, current_patience: float, current_standing: Standing) -> Standing:
        """
        Determines current standing based on patience dynamics and past standing.
        """
        if current_standing == Standing.GOOD:
            if current_patience < self.bad_threshold:
                return Standing.BAD
            return Standing.GOOD
        else:
            # User is in BAD standing: requires exceeding pardon_threshold to regain GOOD status
            if current_patience >= self.pardon_threshold:
                return Standing.GOOD
            return Standing.BAD

