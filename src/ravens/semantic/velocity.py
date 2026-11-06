import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Optional

@dataclass
class HostilityVelocityTracker:
    """
    Tracks the acceleration and momentum of user hostility across multi-turn interactions
    with temporal decay dynamics.
    
    Formula:
        For turn 1: Delta_S_1 = 0.0 (baseline established)
        For turn t > 1:
            dt = max(0.5, current_ts - last_turn_ts)
            time_decay = math.exp(-dt / 120.0)
            time_factor = min(1.0, 5.0 / dt)
            Delta_S_t = max(0.0, S_t - S_{t-1}) * time_factor
            V_t = alpha * Delta_S_t + (1 - alpha) * (V_{t-1} * time_decay)
            Momentum_Multiplier = 1.0 + min(1.0, V_t / 50.0)

    If a user is rapidly escalating their rage over consecutive turns (dt < 5s),
    the velocity filter amplifies boundary enforcement pre-emptively.
    If turns are days apart, velocity dissipates naturally to 0.
    """
    alpha: float = 0.6
    current_velocity: float = 0.0
    last_turn_ts: float = 0.0
    last_monotonic_ts: float = 0.0
    stimulus_history: Deque[float] = field(default_factory=lambda: deque(maxlen=10))

    def record_turn(self, stimulus: float, current_ts: Optional[float] = None) -> float:
        """
        Records a new interaction stimulus and updates the hostility velocity.
        Incorporates monotonic clock intervals and NTP jitter immunity.
        Returns the updated momentum multiplier (>= 1.0).
        """
        now = current_ts if current_ts is not None else time.time()
        mono_now = time.monotonic()
        s = max(0.0, min(100.0, stimulus))

        if not self.stimulus_history or self.last_turn_ts <= 0.0:
            delta_s = 0.0
        else:
            if current_ts is not None:
                raw_dt = now - self.last_turn_ts
            elif self.last_monotonic_ts > 0.0:
                raw_dt = mono_now - self.last_monotonic_ts
            else:
                raw_dt = now - self.last_turn_ts

            if raw_dt < 0.0:
                # NTP backward step or clock jitter: suppress false acceleration
                delta_s = 0.0
            else:
                dt = max(0.5, raw_dt)
                # Velocity decays over idle time (half-life window of 120 seconds)
                time_decay = math.exp(-dt / 120.0)
                self.current_velocity *= time_decay
                # Normalize delta stimulus by interaction frequency
                time_factor = min(1.0, 5.0 / dt)
                delta_s = max(0.0, s - self.stimulus_history[-1]) * time_factor

        self.stimulus_history.append(s)
        self.last_turn_ts = now
        self.last_monotonic_ts = mono_now

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
        self.last_turn_ts = 0.0
        self.stimulus_history.clear()
