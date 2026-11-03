import re
from typing import List, Tuple, Set, Optional, Dict

from .base import BaseEvaluator, ToneEvaluation
from .lexicon import (
    PROFANITY_LEXICON,
    TARGET_PRONOUNS,
    POSITIVE_MODIFIERS,
    CONTRITION_MARKERS,
    COMMON_ACRONYMS,
)
from ..morphology.normalizer import MorphologyNormalizer
from ..semantic.evaluator import SemanticEvaluator

# Known phonetic slang aliases and shorthand abbreviations
PHONETIC_SLANG_ALIASES: Dict[str, str] = {
    "goblog": "goblok",
    "anjir": "anjing",
    "anying": "anjing",
    "anj": "anjing",
    "tolil": "tolol",
    "fak": "fuck",
    "fck": "fuck",
    "bgsd": "bangsat",
    "bgst": "bangsat",
    "kntl": "kontol",
    "mmk": "memek",
    "asw": "asu",
    "jncuk": "jancuk",
}


class HuginnEye(BaseEvaluator):
    """
    The Eye of Huginn: A sub-millisecond heuristic & sociopragmatic tone evaluator.
    
    Equipped with:
    - Adversarial Morphology De-obfuscation (leet-speak, Cyrillic homoglyphs, spaced letters).
    - Sociopragmatic Directedness (Curry & Rieser, 2019).
    - Zero-Profanity Semantic Intent Detection (condescension, existential threats, devaluation).
    """

    def __init__(
        self,
        window_size: int = 3,
        normalizer: Optional[MorphologyNormalizer] = None,
        semantic_evaluator: Optional[SemanticEvaluator] = None,
    ):
        self.window_size = window_size
        self.normalizer = normalizer or MorphologyNormalizer()
        self.semantic_evaluator = semantic_evaluator or SemanticEvaluator()

        # Precompile regex for tokenization
        self._word_pattern = re.compile(r"\b[\w'-]+\b", re.UNICODE)
        self._exclamation_pattern = re.compile(r"!{2,}")

        # Multi-word profanities
        self._multiword_profanities: List[Tuple[str, float]] = [
            (phrase, score) for phrase, score in PROFANITY_LEXICON.items() if " " in phrase
        ]
        self._multiword_contritions: List[str] = [
            phrase for phrase in CONTRITION_MARKERS if " " in phrase
        ]

    def _calculate_shouting_score(self, text: str, tokens: List[str]) -> float:
        total_alpha = 0
        raw_upper_count = 0
        for c in text:
            if c.isalpha():
                total_alpha += 1
                if c.isupper():
                    raw_upper_count += 1

        if total_alpha < 4:
            return 0.0
        
        for token in tokens:
            if token.upper() in COMMON_ACRONYMS:
                raw_upper_count -= len(token)

        adjusted_upper = max(0, raw_upper_count)
        caps_ratio = adjusted_upper / total_alpha

        exclamation_matches = self._exclamation_pattern.findall(text)
        exclamation_bonus = min(0.3, len(exclamation_matches) * 0.15)

        if caps_ratio > 0.45:
            arousal = (caps_ratio - 0.45) / 0.55
            return min(1.0, arousal + exclamation_bonus)
        
        return min(1.0, exclamation_bonus) if caps_ratio > 0.25 else 0.0

    def evaluate(self, text: str) -> ToneEvaluation:
        text_clean = text.strip()
        if not text_clean:
            return ToneEvaluation(
                raw_text=text,
                lexical_score=0.0,
                shouting_score=0.0,
                directedness_score=0.0,
                contrition_score=0.0,
                semantic_score=0.0,
            )

        # 1. Adversarial Morphology Normalization
        normalized_text = self.normalizer.normalize(text_clean)

        tokens_raw = self._word_pattern.findall(normalized_text)
        tokens_lower = [t.lower() for t in tokens_raw]
        text_lower = normalized_text.lower()

        # 2. Multi-word phrase checks
        detected_profanities: List[str] = []
        max_severity = 0.0

        for phrase, score in self._multiword_profanities:
            if phrase in text_lower:
                detected_profanities.append(phrase)
                max_severity = max(max_severity, score)

        # 3. Single-token profanities and phonetic aliases
        profane_indices: List[Tuple[int, str, float]] = []
        for i, token in enumerate(tokens_lower):
            target_token = PHONETIC_SLANG_ALIASES.get(token, token)

            if target_token in PROFANITY_LEXICON:
                severity = PROFANITY_LEXICON[target_token]
                detected_profanities.append(target_token)
                max_severity = max(max_severity, severity)
                profane_indices.append((i, target_token, severity))

        # 4. Sociopragmatic Directedness Evaluation
        has_profanity = len(detected_profanities) > 0
        is_expressive_only = False
        directedness_score = 0.0

        if has_profanity:
            directed_hits = 0
            expressive_hits = 0

            for idx, word, _ in profane_indices:
                start = max(0, idx - self.window_size)
                end = min(len(tokens_lower), idx + self.window_size + 1)
                context_window = set(tokens_lower[start:end])

                is_targeted = bool(context_window & TARGET_PRONOUNS)
                is_positive = bool(context_window & POSITIVE_MODIFIERS)

                if is_targeted:
                    directed_hits += 1
                elif is_positive:
                    expressive_hits += 1

            if directed_hits > 0:
                directedness_score = 1.0
            elif expressive_hits > 0 and directed_hits == 0:
                directedness_score = 0.15
                is_expressive_only = True
            else:
                directedness_score = 0.45

        # 5. Typographical Shouting Detection
        shouting_score = self._calculate_shouting_score(text_clean, tokens_raw)

        # 6. Zero-Profanity Semantic Intent Evaluation
        semantic_result = self.semantic_evaluator.evaluate(normalized_text)
        semantic_score = semantic_result.intent_score
        semantic_intents = [intent.value for intent in semantic_result.matched_intents]

        # 7. Contrition / Apology Detection
        contrition_score = 0.0
        has_contrition = False

        for phrase in self._multiword_contritions:
            if phrase in text_lower:
                has_contrition = True
                break

        if not has_contrition:
            for token in tokens_lower:
                if token in CONTRITION_MARKERS:
                    has_contrition = True
                    break

        if has_contrition:
            # Apology is strictly voided if combined with ANY profanity, ANY hostile semantic intent,
            # or aggressive shouting (Anti-Contrition Smuggling Defense)
            if has_profanity or semantic_score > 0.0 or shouting_score > 0.2:
                contrition_score = 0.0
            else:
                contrition_score = 0.8
                if any(w in tokens_lower for w in ["tolong", "please", "mohon", "bantu"]):
                    contrition_score = 1.0

        return ToneEvaluation(
            raw_text=text_clean,
            lexical_score=max_severity,
            shouting_score=shouting_score,
            directedness_score=directedness_score,
            contrition_score=contrition_score,
            semantic_score=semantic_score,
            detected_profanities=detected_profanities,
            semantic_intents=semantic_intents,
            is_expressive_only=is_expressive_only,
        )
