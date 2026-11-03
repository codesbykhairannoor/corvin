from .homoglyphs import fold_homoglyphs, HOMOGLYPH_MAP
from .cleaners import (
    strip_invisible_characters,
    collapse_elongations,
    collapse_spaced_words,
)
from .zalgo import strip_zalgo, BIDI_CHARS
from .fuzzy import jaro_winkler_similarity
from .normalizer import MorphologyNormalizer

__all__ = [
    "fold_homoglyphs",
    "HOMOGLYPH_MAP",
    "strip_invisible_characters",
    "collapse_elongations",
    "collapse_spaced_words",
    "strip_zalgo",
    "BIDI_CHARS",
    "jaro_winkler_similarity",
    "MorphologyNormalizer",
]
