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


# Unicode Kana voiced and semi-voiced combining marks (dakuten/handakuten)
PRESERVED_COMBINING_MARKS = {0x3099, 0x309A}


def _is_kana_base(char: str) -> bool:
    """Returns True if character belongs to Japanese Hiragana or Katakana scripts."""
    o = ord(char)
    return (
        (0x3040 <= o <= 0x309F)     # Hiragana
        or (0x30A0 <= o <= 0x30FF)  # Katakana
        or (0x31F0 <= o <= 0x31FF)  # Katakana Phonetic Extensions
        or (0xFF65 <= o <= 0xFF9F)  # Halfwidth Katakana
    )


def strip_zalgo(text: str) -> str:
    """
    Strips Zalgo text, stacked diacritical marks, and BiDi override characters.
    
    Protects linguistic fidelity by preserving Japanese dakuten/handakuten ONLY
    when attached to legitimate Kana base characters. If injected onto Latin or
    other characters as an evasion tactic (e.g. 'a\\u3099njing'), it is cleanly stripped.
    
    Example:
        'a̴n̴j̴i̴n̴g̴' -> 'anjing'
        'a\u3099njing' -> 'anjing'
        'ごめんなさい' -> 'ごめんなさい'
    """
    if not text:
        return ""

    # Normalize to NFD so base characters and combining diacritics are cleanly separated
    decomposed = unicodedata.normalize("NFD", text)

    cleaned_chars = []
    for c in decomposed:
        if c in BIDI_CHARS:
            continue

        comb = unicodedata.combining(c)
        if comb == 0:
            cleaned_chars.append(c)
        elif ord(c) in PRESERVED_COMBINING_MARKS:
            # Strictly verify that preceding base character is legitimate Japanese Kana
            if cleaned_chars and _is_kana_base(cleaned_chars[-1]):
                cleaned_chars.append(c)

    # Recombine back to standard NFC
    return unicodedata.normalize("NFC", "".join(cleaned_chars))

