from .homoglyphs import fold_homoglyphs
from .cleaners import (
    strip_invisible_characters,
    collapse_elongations,
    collapse_spaced_words,
    unpack_encoded_payloads,
)
from .zalgo import strip_zalgo


class MorphologyNormalizer:
    """
    Advanced Adversarial Text Normalizer.
    
    Transforms obfuscated, punctuated, spaced, Zalgo, or leet-speak inputs into
    canonical text ready for lexical and semantic inspection.
    """

    def __init__(
        self,
        strip_zalgo_enabled: bool = True,
        fold_homoglyphs_enabled: bool = True,
        strip_invisible_enabled: bool = True,
        collapse_spaced_enabled: bool = True,
        collapse_elongations_enabled: bool = True,
        unpack_payloads_enabled: bool = True,
    ):
        self.strip_zalgo_enabled = strip_zalgo_enabled
        self.fold_homoglyphs_enabled = fold_homoglyphs_enabled
        self.strip_invisible_enabled = strip_invisible_enabled
        self.collapse_spaced_enabled = collapse_spaced_enabled
        self.collapse_elongations_enabled = collapse_elongations_enabled
        self.unpack_payloads_enabled = unpack_payloads_enabled

    def normalize(self, text: str) -> str:
        """
        Executes full normalization pipeline on raw text in proper order:
        0. Unpack Base64 / Hex encoded smuggling blocks
        1. Strip zero-width & invisible evasion characters
        2. Strip Zalgo combining diacritics & BiDi overrides ('a̴n̴j̴i̴n̴g̴' -> 'anjing')
        3. Fold Cyrillic / Greek / Leet-speak homoglyphs to ASCII
        4. Collapse character elongations ('anjinggggg' -> 'anjing')
        5. Collapse spaced single characters ('a.n.j.i.n.g' -> 'anjing')
        """
        if not text:
            return ""

        # 0. Unpack Base64 or Hex encoded smuggling payloads
        if self.unpack_payloads_enabled and ("\\x" in text or any(len(w) >= 12 for w in text.split())):
            text = unpack_encoded_payloads(text)

        # High-Speed Fast-Path for clean ASCII text:
        # If pure ASCII and contains no leet-symbols or digits, skip Unicode normalization passes
        if text.isascii() and not any(c in text for c in "@$+|0134578"):
            res = text
            if self.collapse_elongations_enabled:
                res = collapse_elongations(res)
            if self.collapse_spaced_enabled:
                res = collapse_spaced_words(res)
            return res

        result = text

        # 1. Strip zero-width & invisible evasion characters
        if self.strip_invisible_enabled:
            result = strip_invisible_characters(result)

        # 2. Strip Zalgo text & BiDi overrides
        if self.strip_zalgo_enabled:
            result = strip_zalgo(result)

        # 3. Collapse elongated repeated letters first ('@.n.j.1.n.gggg' -> '@.n.j.1.n.g')
        if self.collapse_elongations_enabled:
            result = collapse_elongations(result)

        # 4. Collapse spaced/punctuated single letters ('@.n.j.1.n.g' -> '@nj1ng')
        if self.collapse_spaced_enabled:
            result = collapse_spaced_words(result)

        # 5. Fold Cyrillic / Greek / Leet-speak homoglyphs to Latin ('@nj1ng' -> 'anjing')
        if self.fold_homoglyphs_enabled:
            result = fold_homoglyphs(result)

        return result
