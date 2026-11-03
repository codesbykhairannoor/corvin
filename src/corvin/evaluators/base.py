from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

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
    is_expressive_only: bool = False  # True if profanity was used positively (e.g. "anjing keren")

    @property
    def composite_raw_stimulus(self) -> float:
        """
        Combines lexical, shouting, directedness, and zero-profanity semantic intent into [0.0, 1.0].
        If expressive only, stimulus is dampened to near-zero.
        """
        if self.is_expressive_only:
            return 0.05 * self.lexical_score

        # Directedness amplifies or dampens lexical impact
        directed_lexical = self.lexical_score * self.directedness_score
        lexical_component = min(1.0, (0.55 * directed_lexical) + (0.45 * self.shouting_score))

        # Take the maximum between overt lexical abuse and covert semantic abuse
        return min(1.0, max(lexical_component, self.semantic_score))


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
