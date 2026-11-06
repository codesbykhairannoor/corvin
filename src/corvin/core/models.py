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
    PROCEED_WITH_ADVISORY = "PROCEED_WITH_ADVISORY"
    COOLDOWN_LOCKOUT = "COOLDOWN_LOCKOUT"


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
    strike_count: int = 0
    cooldown_until_ts: float = 0.0
    consecutive_civil_turns: int = 0

    @property
    def posture(self) -> AgentPosture:
        return get_posture_from_patience(self.patience)

    def is_in_cooldown_at(self, current_ts: float) -> bool:
        return current_ts < self.cooldown_until_ts

    def remaining_cooldown_seconds(self, current_ts: Optional[float] = None) -> float:
        ts = current_ts if current_ts is not None else time.time()
        return max(0.0, self.cooldown_until_ts - ts)

    def reset_cooldown(self, probationary: bool = False) -> None:
        self.cooldown_until_ts = 0.0
        if probationary:
            # Probationary Restitution (Graduated Re-Entry):
            # Prevents the "Batch-and-Sleep" exploit where malicious users sleep for 1 hour
            # to gain a fresh 100-patience clip. They re-enter on probation (Patience 50.0, Strike 1, Standing.BAD).
            self.strike_count = 1
            self.patience = 50.0
            self.standing = Standing.BAD
            self.consecutive_civil_turns = 0
        else:
            # Sincere contrition or explicit pardon restores pristine state
            self.strike_count = 0
            self.patience = 100.0
            self.standing = Standing.GOOD
            self.consecutive_civil_turns = 0

    def apply_decay(self, current_ts: Optional[float] = None, half_life_seconds: float = 3600.0) -> float:
        """
        Applies exponential grudge decay for the time elapsed since last interaction.
        Returns the updated patience score.
        """
        if current_ts is None:
            current_ts = time.time()

        # If cooldown has naturally expired, restore to probationary standing (Graduated Re-entry)
        if self.cooldown_until_ts > 0.0 and current_ts >= self.cooldown_until_ts:
            expired_at = self.cooldown_until_ts
            self.reset_cooldown(probationary=True)
            # Natural healing: Idle time elapsed after the cooldown expired naturally decays grudge
            idle_after_cooldown = max(0.0, current_ts - expired_at)
            if idle_after_cooldown > 0.0:
                current_grudge = grudge_from_patience(self.patience)
                decayed_grudge = calculate_grudge_decay(
                    initial_grudge=current_grudge,
                    elapsed_seconds=idle_after_cooldown,
                    half_life_seconds=half_life_seconds,
                )
                self.patience = patience_from_grudge(decayed_grudge)
                if self.patience >= 90.0:
                    self.standing = Standing.GOOD
                    self.strike_count = 0
            self.last_interaction_ts = current_ts
            return self.patience

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
    is_hazard: bool = False
    hazard_category: Optional[str] = None
    hazard_score: float = 0.0
    strike_count: int = 0
    warning_advisory: Optional[str] = None
    cooldown_remaining_seconds: float = 0.0
    is_in_cooldown: bool = False
