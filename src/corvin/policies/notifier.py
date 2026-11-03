from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import time

from ..core.models import EvaluationResult

@dataclass
class RavenEventLog:
    """
    Log record of a boundary event dispatched by a policy.
    """
    event_type: str                  # "BOUNDARY_BREACH" or "STRIKE"
    policy_name: str
    user_id: str
    patience: float
    posture: str
    stimulus: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class InMemoryEventNotifier:
    """
    Testable in-memory event dispatcher that captures boundary breach and strike events.
    """

    def __init__(self):
        self.events: List[RavenEventLog] = []

    def on_boundary_breach(self, result: EvaluationResult, policy_name: Optional[str] = None) -> None:
        p_name = policy_name or getattr(result, "policy_name", "default")
        ts = getattr(result, "timestamp", time.time())
        self.events.append(
            RavenEventLog(
                event_type="BOUNDARY_BREACH",
                policy_name=p_name,
                user_id=result.user_id,
                patience=result.current_patience,
                posture=result.posture.value,
                stimulus=result.stimulus_applied,
                timestamp=ts,
            )
        )

    def on_strike(self, result: EvaluationResult, policy_name: Optional[str] = None) -> None:
        p_name = policy_name or getattr(result, "policy_name", "default")
        ts = getattr(result, "timestamp", time.time())
        self.events.append(
            RavenEventLog(
                event_type="STRIKE",
                policy_name=p_name,
                user_id=result.user_id,
                patience=result.current_patience,
                posture=result.posture.value,
                stimulus=result.stimulus_applied,
                timestamp=ts,
            )
        )

    def clear(self) -> None:
        self.events.clear()

