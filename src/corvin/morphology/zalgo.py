import unicodedata
from typing import Set

# Unicode BiDi (Bidirectional) override and control characters
BIDI_CHARS: Set[str] = {
    "\u202A",  # Left-to-Right Embedding (LRE)
    "\u202B",  # Right-to-Left Embedding (RLE)
    "\u202C",  # Pop Directional Formatting (PDF)
    "\u202D",  # Left-to-Right Override (LRO)
    "\u202E",  # Right-to-Left Override (RLO)
    "\u2066",  # Left-to-Right Isolate (LRI)
    "\u2067",  # Right-to-Left Isolate (RLI)
    "\u2068",  # First Strong Isolate (FSI)
    "\u2069",  # Pop Directional Isolate (PDI)
}


# Unicode Kana voiced and semi-voiced combining marks that must be preserved
PRESERVED_COMBINING_MARKS = {0x3099, 0x309A}


def strip_zalgo(text: str) -> str:
    """
    Strips Zalgo text, stacked diacritical marks, and BiDi override characters.
    
    Example:
        'a̴n̴j̴i̴n̴g̴' -> 'anjing'
        't\u0334o\u0335l\u0336o\u0337l' -> 'tolol'
    """
    if not text:
        return ""

    # Normalize to NFD so base characters and combining diacritics are cleanly separated
    decomposed = unicodedata.normalize("NFD", text)

    # Filter out combining diacritical marks (unicodedata.combining > 0) and BiDi controls,
    # while preserving phonemic script characters like Japanese Kana dakuten/handakuten.
    cleaned_chars = [
        c for c in decomposed
        if (unicodedata.combining(c) == 0 or ord(c) in PRESERVED_COMBINING_MARKS) and c not in BIDI_CHARS
    ]

    # Recombine back to standard NFC
    return unicodedata.normalize("NFC", "".join(cleaned_chars))

