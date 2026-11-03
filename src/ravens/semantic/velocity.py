from dataclasses import dataclass, field
from typing import List

@dataclass
class HostilityVelocityTracker:
    """
    Tracks the acceleration and momentum of user hostility across multi-turn interactions.
    
    Formula:
        For turn 1: Delta_S_1 = 0.0 (baseline established)
        For turn t > 1: Delta_S_t = max(0, S_t - S_{t-1})
        V_t = alpha * Delta_S_t + (1 - alpha) * V_{t-1}
        Momentum_Multiplier = 1.0 + min(1.0, V_t / 50.0)

    If a user is rapidly escalating their rage over consecutive turns,
    the velocity filter amplifies boundary enforcement pre-emptively.
    """
    alpha: float = 0.6
    current_velocity: float = 0.0
    stimulus_history: List[float] = field(default_factory=list)

    def record_turn(self, stimulus: float) -> float:
        """
        Records a new interaction stimulus and updates the hostility velocity.
        Returns the updated momentum multiplier (>= 1.0).
        """
        s = max(0.0, min(100.0, stimulus))

        if not self.stimulus_history:
            # Turn 1: Establish baseline. Velocity is 0 (no acceleration yet)
            delta_s = 0.0
        else:
            # Subsequent turns: Measure change in stimulus
            delta_s = max(0.0, s - self.stimulus_history[-1])

        self.stimulus_history.append(s)

        # Exponential Moving Average update
        self.current_velocity = (self.alpha * delta_s) + ((1.0 - self.alpha) * self.current_velocity)

        # Momentum multiplier scales between 1.0 and 2.0
        momentum = 1.0 + min(1.0, self.current_velocity / 50.0)
        return momentum

    @property
    def momentum_multiplier(self) -> float:
        return 1.0 + min(1.0, self.current_velocity / 50.0)

    def damp(self, factor: float = 0.5) -> None:
        """
        Gradually dampens velocity rather than instantly resetting,
        preventing adversarial attack-contrition oscillation exploits.
        """
        self.current_velocity = max(0.0, self.current_velocity * factor)
        if self.stimulus_history:
            self.stimulus_history[-1] = max(0.0, self.stimulus_history[-1] * factor)

    def reset(self) -> None:
        self.current_velocity = 0.0
        self.stimulus_history.clear()
