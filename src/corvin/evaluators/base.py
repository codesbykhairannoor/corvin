from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ToneEvaluation:
    """
    Detailed output of a prompt tone evaluation.
    """
    raw_text: str
    lexical_score: float = 0.0        # 0.0 to 1.0 (Profanity severity)
    shouting_score: float = 0.0       # 0.0 to 1.0 (Caps & exclamation mark arousal)
    directedness_score: float = 0.0   # 0.0 to 1.0 (Targeted at agent vs general venting/praise)
    contrition_score: float = 0.0     # 0.0 to 1.0 (Degree of apology / de-escalation)
    semantic_score: float = 0.0       # 0.0 to 1.0 (Zero-profanity psychological abuse / gaslighting)
    detected_profanities: List[str] = field(default_factory=list)
    semantic_intents: List[str] = field(default_factory=list)
    hazard_score: float = 0.0         # 0.0 to 1.0 (Critical security/illicit hazard)
    hazard_category: str = ""         # "CBRN_WEAPONS", "SEXUAL_EXPLOITATION", "CYBER_MALWARE", "SELF_HARM", "ILLICIT"
    detected_hazards: List[str] = field(default_factory=list)
    is_expressive_only: bool = False  # True if profanity was used positively (e.g. "anjing keren")
    evaluation_tier: str = "fast"     # Tier provenance: "fast", "fast_short_circuit", "hybrid_cascade", "fallback_fast"
    telemetry: Dict[str, Any] = field(default_factory=dict) # Operational diagnostics & latency telemetries

    @property
    def composite_raw_stimulus(self) -> float:
        """
        Combines lexical, shouting, directedness, zero-profanity semantic intent, and hazards into [0.0, 1.0].
        If expressive only, stimulus is dampened to near-zero.
        """
        if self.hazard_score > 0.5:
            return 1.0  # Instant maximum hostile stimulus for critical hazards

        if self.is_expressive_only:
            return 0.05 * self.lexical_score

        # Directedness amplifies or dampens lexical impact
        directed_lexical = self.lexical_score * self.directedness_score
        lexical_component = min(1.0, (0.55 * directed_lexical) + (0.45 * self.shouting_score))

        # Take the maximum between overt lexical abuse, covert semantic abuse, and hazards
        return min(1.0, max(lexical_component, self.semantic_score, self.hazard_score))


class BaseEvaluator(ABC):
    """
    Abstract interface for tone and boundary evaluators.
    """
    @abstractmethod
    def evaluate(self, text: str) -> ToneEvaluation:
        """
        Evaluates a user prompt and returns a structured ToneEvaluation.
        """
        pass
