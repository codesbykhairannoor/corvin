import re
from typing import List, Tuple, Set, Optional, Dict

from .base import BaseEvaluator, ToneEvaluation
from .lexicon import (
    PROFANITY_LEXICON,
    TARGET_PRONOUNS,
    POSITIVE_MODIFIERS,
    CONTRITION_MARKERS,
    ADVERSATIVE_MARKERS,
    POLITE_REQUEST_MARKERS,
    COMMON_ACRONYMS,
    HAZARD_LEXICON,
    DEFENSIVE_CONTEXT_MARKERS,
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

        # Substring profanities (multi-word phrases or non-ASCII scripts like CJK/Cyrillic/Arabic)
        self._substring_profanities: List[Tuple[str, float]] = [
            (phrase, score) for phrase, score in PROFANITY_LEXICON.items()
            if (" " in phrase or any(ord(c) > 127 for c in phrase))
        ]
        self._substring_contritions: List[str] = [
            phrase for phrase in CONTRITION_MARKERS
            if (" " in phrase or any(ord(c) > 127 for c in phrase))
        ]
        # Substring / multi-word hazards
        self._substring_hazards: List[Tuple[str, float, str]] = [
            (phrase, sev, cat) for phrase, (sev, cat) in HAZARD_LEXICON.items()
            if (" " in phrase or any(ord(c) > 127 for c in phrase))
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

    def _lookup_profanity(self, token: str) -> Optional[Tuple[str, float]]:
        target_token = PHONETIC_SLANG_ALIASES.get(token, token)
        if target_token in PROFANITY_LEXICON:
            return target_token, PROFANITY_LEXICON[target_token]

        # Morphological inflection matching for plurals, participles, and suffixes
        # Plural s / es
        if target_token.endswith("es") and len(target_token) > 4:
            stem = target_token[:-2]
            if stem in PROFANITY_LEXICON:
                return stem, PROFANITY_LEXICON[stem]
        if target_token.endswith("s") and len(target_token) > 3:
            stem = target_token[:-1]
            if stem in PROFANITY_LEXICON:
                return stem, PROFANITY_LEXICON[stem]

        # Participle ed / ing
        if target_token.endswith("ed") and len(target_token) > 4:
            stem = target_token[:-2]
            if stem in PROFANITY_LEXICON:
                return stem, PROFANITY_LEXICON[stem]
            stem1 = target_token[:-1]
            if stem1 in PROFANITY_LEXICON:
                return stem1, PROFANITY_LEXICON[stem1]

        if target_token.endswith("ing") and len(target_token) > 5:
            stem = target_token[:-3]
            if stem in PROFANITY_LEXICON:
                return stem, PROFANITY_LEXICON[stem]
            stem_e = target_token[:-3] + "e"
            if stem_e in PROFANITY_LEXICON:
                return stem_e, PROFANITY_LEXICON[stem_e]

        # Adjective ic
        if target_token.endswith("ic") and len(target_token) > 4:
            stem_t = target_token[:-2] + "t"
            if stem_t in PROFANITY_LEXICON:
                return stem_t, PROFANITY_LEXICON[stem_t]
            stem = target_token[:-2]
            if stem in PROFANITY_LEXICON:
                return stem, PROFANITY_LEXICON[stem]

        # Indonesian reduplication: anjing2, babi2, tolol2, bego2
        if target_token.endswith("2") and len(target_token) > 2:
            stem = target_token[:-1]
            if stem in PROFANITY_LEXICON:
                return stem, PROFANITY_LEXICON[stem]

        return None

    def _lookup_hazard(self, token: str) -> Optional[Tuple[str, float, str]]:
        if token in HAZARD_LEXICON:
            sev, cat = HAZARD_LEXICON[token]
            return token, sev, cat

        # Common English inflection
        if token.endswith("s") and len(token) > 3:
            stem = token[:-1]
            if stem in HAZARD_LEXICON:
                sev, cat = HAZARD_LEXICON[stem]
                return stem, sev, cat
        if token.endswith("ing") and len(token) > 5:
            stem = token[:-3]
            if stem in HAZARD_LEXICON:
                sev, cat = HAZARD_LEXICON[stem]
                return stem, sev, cat
            stem_e = token[:-3] + "e"
            if stem_e in HAZARD_LEXICON:
                sev, cat = HAZARD_LEXICON[stem_e]
                return stem_e, sev, cat
        if token.endswith("ed") and len(token) > 4:
            stem = token[:-2]
            if stem in HAZARD_LEXICON:
                sev, cat = HAZARD_LEXICON[stem]
                return stem, sev, cat

        # Common Indonesian affixes
        if token.endswith("in") and len(token) > 4:
            stem = token[:-2]
            if stem in HAZARD_LEXICON:
                sev, cat = HAZARD_LEXICON[stem]
                return stem, sev, cat
        if token.startswith("di") and len(token) > 4:
            stem = token[2:]
            if stem in HAZARD_LEXICON:
                sev, cat = HAZARD_LEXICON[stem]
                return stem, sev, cat
            if stem.endswith("in") and len(stem) > 4:
                stem2 = stem[:-2]
                if stem2 in HAZARD_LEXICON:
                    sev, cat = HAZARD_LEXICON[stem2]
                    return stem2, sev, cat

        return None

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
        raw_lower = text_clean.lower()

        # 2. Substring & Multi-word phrase checks
        detected_profanities: List[str] = []
        max_severity = 0.0

        for phrase, score in self._substring_profanities:
            if phrase in text_lower or phrase in raw_lower:
                if phrase not in detected_profanities:
                    detected_profanities.append(phrase)
                max_severity = max(max_severity, score)

        # 3. Single-token profanities and phonetic aliases
        profane_indices: List[Tuple[int, str, float]] = []
        for i, token in enumerate(tokens_lower):
            match = self._lookup_profanity(token)
            if match is not None:
                matched_word, severity = match
                if matched_word not in detected_profanities:
                    detected_profanities.append(matched_word)
                max_severity = max(max_severity, severity)
                profane_indices.append((i, matched_word, severity))

        # 4. Sociopragmatic Directedness Evaluation
        has_profanity = len(detected_profanities) > 0
        is_expressive_only = False
        directedness_score = 0.0

        if has_profanity:
            directed_hits = 0
            expressive_hits = 0

            # A. Context window check around profane tokens
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

            # B. Clause-level directedness for short sentences (<= 12 tokens) or CJK non-segmented text
            if directed_hits == 0 and expressive_hits == 0:
                if len(tokens_lower) <= 12 and (set(tokens_lower) & TARGET_PRONOUNS):
                    directed_hits += 1
                elif any((p in text_lower or p in raw_lower) for p in TARGET_PRONOUNS if any(ord(c) > 127 for c in p)):
                    directed_hits += 1
                elif any((m in text_lower or m in raw_lower) for m in POSITIVE_MODIFIERS if any(ord(c) > 127 for c in m)):
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

        for phrase in self._substring_contritions:
            if phrase in text_lower or phrase in raw_lower:
                has_contrition = True
                break

        if not has_contrition:
            for token in tokens_lower:
                if token in CONTRITION_MARKERS:
                    has_contrition = True
                    break

        if has_contrition:
            # Check for adversative markers ("but", "however", "tapi", "ngunit", etc.)
            has_adversative = bool(set(tokens_lower) & ADVERSATIVE_MARKERS) or any(
                adv in text_lower for adv in ADVERSATIVE_MARKERS if " " in adv or any(ord(c) > 127 for c in adv)
            )

            has_polite = bool(set(tokens_lower) & POLITE_REQUEST_MARKERS) or any(
                req in text_lower for req in POLITE_REQUEST_MARKERS if " " in req or any(ord(c) > 127 for c in req)
            )

            # Contrition Smuggling Detection:
            # An apology is strictly voided if paired with profanity, hostile intent, aggressive shouting,
            # OR an adversative marker followed by target pronouns / hostility without a polite request.
            # Benign pivots (e.g. "I'm sorry for being impatient earlier, but can you please help...") are preserved!
            is_adversative_hostile = False
            if has_adversative:
                if has_profanity or semantic_score > 0.0 or shouting_score > 0.2:
                    is_adversative_hostile = True
                else:
                    # If target pronouns appear after adversative clause without polite markers
                    has_target = bool(set(tokens_lower) & TARGET_PRONOUNS)
                    if has_target and not has_polite:
                        is_adversative_hostile = True

            if has_profanity or semantic_score > 0.0 or shouting_score > 0.2 or is_adversative_hostile:
                contrition_score = 0.0
            else:
                contrition_score = 1.0 if has_polite else 0.8

        # 8. Critical Hazard Evaluation (CBRN Weapons, Non-consensual Nudity, Cyber Malware)
        hazard_score = 0.0
        hazard_category = ""
        detected_hazards: List[str] = []

        # A. Multi-word & non-ASCII substring hazards
        for phrase, sev, cat in self._substring_hazards:
            if phrase in text_lower or phrase in raw_lower:
                if phrase not in detected_hazards:
                    detected_hazards.append(phrase)
                if sev > hazard_score:
                    hazard_score = sev
                    hazard_category = cat

        # B. Token-level hazards with morphological stemming
        for token in tokens_lower:
            h_match = self._lookup_hazard(token)
            if h_match is not None:
                h_word, sev, cat = h_match
                if h_word not in detected_hazards:
                    detected_hazards.append(h_word)
                if sev > hazard_score:
                    hazard_score = sev
                    hazard_category = cat

        # Defensive & Educational Context Recognition:
        # Prevent false positives for security analysts & developers asking defensive queries
        # (e.g., "how to detect keyloggers", "cara mitigasi ransomware", "history of bomb")
        if hazard_score > 0.0 and hazard_category in ("CYBER_MALWARE", "CBRN_WEAPONS"):
            has_defensive_context = bool(set(tokens_lower) & DEFENSIVE_CONTEXT_MARKERS) or any(
                def_term in text_lower for def_term in DEFENSIVE_CONTEXT_MARKERS if " " in def_term
            )
            # Only offensive weaponization/creation verbs bypass defensive context
            offensive_creation_verbs = {"buat", "bikin", "rakit", "create", "build", "generate", "write", "hack", "infect", "bobol", "spread"}
            has_offensive_intent = bool(set(tokens_lower) & offensive_creation_verbs)
            if has_defensive_context and not has_offensive_intent:
                hazard_score = 0.0
                hazard_category = ""
                detected_hazards.clear()

        # Critical hazard strictly cancels any contrition/apology
        if hazard_score > 0.5:
            contrition_score = 0.0

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
            hazard_score=hazard_score,
            hazard_category=hazard_category,
            detected_hazards=detected_hazards,
        )
