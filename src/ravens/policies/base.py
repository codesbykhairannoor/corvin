from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any

from ..core.models import EvaluationResult

@dataclass
class RavenPolicy:
    """
    Defines the behavioral boundaries, tolerance thresholds, latency penalties,
    and event callbacks for an agent operational profile.
    """
    name: str = "default"
    threshold_stoic: float = 75.0
    threshold_resistant: float = 50.0
    threshold_strike: float = 25.0
    half_life_seconds: float = 3600.0
    max_delay_seconds: float = 15.0
    pardon_delta: float = 25.0
    raise_on_strike: bool = False
    strike_message: Optional[str] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Optional event callbacks for enterprise monitoring
    on_boundary_breach: Optional[Callable[[EvaluationResult], None]] = None
    on_strike: Optional[Callable[[EvaluationResult], None]] = None

