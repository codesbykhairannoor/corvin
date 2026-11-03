"""
Hybrid Cascaded Evaluator: SOTA Two-Tier Fast-Path / Slow-Path Architecture.
Combines sub-millisecond local heuristics (<0.1ms) with universal multi-lingual moderation.
"""

from typing import Optional, List
from .base import BaseEvaluator, ToneEvaluation
from .heuristic import HuginnEye


class HybridEvaluator(BaseEvaluator):
    """
    Two-Tier Speculative Fast-Path / Slow-Path Evaluator.
    
    Operational Flow:
    1. Layer 1 (Fast-Path Local, <0.1ms, $0):
       Evaluates via local HuginnEye (Normalizer, Zalgo, Homoglyphs, Multilingual Lexicon, Caps/Shouting).
       If severe hostility is detected (stimulus >= fast_abort_threshold) -> Returns immediately!
       Zero network latency, zero external API calls.
    2. Layer 2 (Universal Slow-Path Fallback):
       If Layer 1 is below the fast abort threshold AND slow_evaluator is configured,
       delegates to slow_evaluator (e.g. OpenAIModerationEvaluator for 100+ languages).
    """

    def __init__(
        self,
        fast_evaluator: Optional[BaseEvaluator] = None,
        slow_evaluator: Optional[BaseEvaluator] = None,
        fast_abort_threshold: float = 0.45,
    ):
        self.fast_evaluator = fast_evaluator or HuginnEye()
        self.slow_evaluator = slow_evaluator
        self.fast_abort_threshold = fast_abort_threshold

    def evaluate(self, text: str) -> ToneEvaluation:
        # Step 1: Run sub-millisecond local fast-path
        fast_result = self.fast_evaluator.evaluate(text)

        # If fast-path detected strong hostility, short-circuit immediately!
        if fast_result.composite_raw_stimulus >= self.fast_abort_threshold:
            return fast_result

        # If no slow evaluator configured, return fast path result
        if self.slow_evaluator is None:
            return fast_result

        # Step 2: Fallback to universal multi-lingual slow-path
        try:
            slow_result = self.slow_evaluator.evaluate(text)
        except Exception:
            # Bulletproof fallback: If external evaluator fails or times out, safely return fast path
            return fast_result

        # Merge results: take maximum hostility while preserving contrition & profanities
        merged_lexical = max(fast_result.lexical_score, slow_result.lexical_score)
        merged_semantic = max(fast_result.semantic_score, slow_result.semantic_score)
        merged_directedness = max(fast_result.directedness_score, slow_result.directedness_score)
        merged_shouting = max(fast_result.shouting_score, slow_result.shouting_score)
        merged_contrition = max(fast_result.contrition_score, slow_result.contrition_score)

        merged_profanities = list(set(fast_result.detected_profanities + slow_result.detected_profanities))
        merged_intents = list(set(fast_result.semantic_intents + slow_result.semantic_intents))

        return ToneEvaluation(
            raw_text=text,
            lexical_score=merged_lexical,
            shouting_score=merged_shouting,
            directedness_score=merged_directedness,
            contrition_score=merged_contrition,
            semantic_score=merged_semantic,
            detected_profanities=merged_profanities,
            semantic_intents=merged_intents,
            is_expressive_only=fast_result.is_expressive_only,
        )
