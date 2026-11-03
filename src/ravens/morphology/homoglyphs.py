import re
import unicodedata
from typing import Dict

# Common Cyrillic and symbol homoglyphs mapped to ASCII Latin
HOMOGLYPH_MAP: Dict[str, str] = {
    # Cyrillic lowercase
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "p", "с": "c", "т": "t", "у": "y", "ф": "f",
    "х": "x", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sh", "ъ": "", "ы": "y",
    "ь": "", "э": "e", "ю": "yu", "я": "ya", "і": "i", "ј": "j",
    
    # Cyrillic uppercase
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O",
    "Р": "P", "С": "C", "Т": "T", "У": "Y", "Х": "X",

    # Symbols (Punctuation like '!' is excluded to preserve sentence structure)
    "@": "a",
    "$": "s",
    "+": "t",
    "|": "l",
}

# Leet-speak digit substitutions that should ONLY be folded in mixed alphanumeric contexts
# Standalone numbers (e.g. '400', '123', '3.14') must NEVER be mutated to corrupt benign code.
LEET_DIGIT_MAP: Dict[str, str] = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
}

# Regex to detect tokens containing digits mixed with letters or leet symbols
_MIXED_LEET_TOKEN_REGEX = re.compile(r"\b(?=\w*\d)(?=\w*[a-zA-Z@$+|])\w+\b")


def fold_homoglyphs(text: str) -> str:
    """
    De-obfuscates text by mapping visually identical Cyrillic, Greek,
    and Leet-speak glyphs back to standard ASCII Latin characters.
    
    Preserves benign pure-numeric tokens (e.g. '400', '3.14') to prevent
    corrupting technical code and parameters.
    """
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKD", text)

    # 1. Map Cyrillic and symbols
    chars = [HOMOGLYPH_MAP.get(c, c) for c in normalized]
    mapped_text = "".join(chars)

    # 2. Map leet digits only inside mixed alphanumeric tokens (e.g. '@nj1ng' -> 'anjing')
    def _fold_leet_match(match: re.Match) -> str:
        word = match.group(0)
        return "".join(LEET_DIGIT_MAP.get(c, c) for c in word)

    return _MIXED_LEET_TOKEN_REGEX.sub(_fold_leet_match, mapped_text)
