import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any

from .standing import Standing
from .state import AgentPosture, get_posture_from_patience
from ..math.decay import calculate_grudge_decay, patience_from_grudge, grudge_from_patience

class ActionDecision(str, Enum):
    PROCEED = "PROCEED"
    DELAY_AND_PROCEED = "DELAY_AND_PROCEED"
    HALT_STRIKE = "HALT_STRIKE"


@dataclass
class UserPatienceProfile:
    """
    Stateful persistence profile for a user across conversational sessions.
    """
    user_id: str
    patience: float = 100.0
    standing: Standing = Standing.GOOD
    infraction_count: int = 0
    last_interaction_ts: float = field(default_factory=time.time)
    created_at_ts: float = field(default_factory=time.time)

    @property
    def posture(self) -> AgentPosture:
        return get_posture_from_patience(self.patience)

    def apply_decay(self, current_ts: Optional[float] = None, half_life_seconds: float = 3600.0) -> float:
        """
        Applies exponential grudge decay for the time elapsed since last interaction.
        Returns the updated patience score.
        """
        if current_ts is None:
            current_ts = time.time()

        elapsed = max(0.0, current_ts - self.last_interaction_ts)
        current_grudge = grudge_from_patience(self.patience)
        decayed_grudge = calculate_grudge_decay(
            initial_grudge=current_grudge,
            elapsed_seconds=elapsed,
            half_life_seconds=half_life_seconds,
        )
        new_patience = patience_from_grudge(decayed_grudge)
        self.patience = new_patience
        self.last_interaction_ts = current_ts
        return new_patience


@dataclass
class EvaluationResult:
    """
    The output of an interaction evaluation.
    """
    user_id: str
    prior_patience: float
    current_patience: float
    stimulus_applied: float
    posture: AgentPosture
    standing: Standing
    delay_seconds: float
    decision: ActionDecision
    system_directive: Optional[str]
    strike_message: Optional[str] = None
    friction_directive: Optional[Any] = None
    policy_name: str = "default"
    timestamp: float = field(default_factory=time.time)
