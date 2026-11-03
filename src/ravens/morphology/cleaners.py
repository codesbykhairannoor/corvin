import re
from typing import List, Set

# Zero-width, formatting, and invisible characters
INVISIBLE_CHARS: Set[str] = {
    "\u200B",  # Zero-width space
    "\u200C",  # Zero-width non-joiner
    "\u200D",  # Zero-width joiner
    "\uFEFF",  # Byte order mark / zero-width no-break space
    "\u00AD",  # Soft hyphen
    "\u2060",  # Word joiner
    "\u200E",  # Left-to-right mark
    "\u200F",  # Right-to-left mark
}

# Regex to find characters repeated 3 or more times (e.g. "gooooblooookkkk")
ELONGATION_REGEX = re.compile(r"([a-zA-Z])\1{2,}", re.IGNORECASE)

# Regex to detect single characters separated by dots, dashes, underscores, slashes, or spaces
# e.g., "a.n.j.i.n.g", "b-a-n-g-s-a-t", "t o l o l", "@.n.j.1.n.g"
SPACED_LETTERS_REGEX = re.compile(
    r"(?:^|(?<=\s))(?:[a-zA-Z0-9@$+|][\.\-_/ ]){2,}[a-zA-Z0-9@$+|](?=\s|[!?,.]|$)",
    re.IGNORECASE
)


def strip_invisible_characters(text: str) -> str:
    """
    Removes zero-width and invisible unicode characters injected to bypass text filters.
    """
    return "".join(c for c in text if c not in INVISIBLE_CHARS)


def collapse_elongations(text: str, max_repeat: int = 1) -> str:
    """
    Collapses exaggerated character repetitions.
    Example: 'anjinggggg' -> 'anjing', 'toloooool' -> 'tolol'
    """
    def _repl(match):
        char = match.group(1)
        return char * max_repeat

    return ELONGATION_REGEX.sub(_repl, text)


def collapse_spaced_words(text: str) -> str:
    """
    Reconstructs words that have been deliberately spaced or punctuated to fool tokenizers.
    Example: 'a.n.j.i.n.g' -> 'anjing', 'b-a-n-g-s-a-t' -> 'bangsat', 't o l o l' -> 'tolol'
    """
    def _repl(match):
        segment = match.group(0)
        # Strip all punctuation and whitespace between the single characters
        cleaned = re.sub(r"[\.\-_/ ]+", "", segment)
        return cleaned

    return SPACED_LETTERS_REGEX.sub(_repl, text)
