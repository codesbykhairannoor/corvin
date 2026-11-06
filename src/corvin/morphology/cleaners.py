import base64
import re
import unicodedata
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
    "\u180E",  # Mongolian vowel separator
    "\u034F",  # Combining grapheme joiner
    "\u2800",  # Braille blank
}

# Regex to find characters repeated 3 or more times (e.g. "gooooblooookkkk")
ELONGATION_REGEX = re.compile(r"([a-zA-Z])\1{2,}", re.IGNORECASE)

# Regex to detect single characters separated by dots, dashes, underscores, slashes, or multiple spaces
# e.g., "a.n.j.i.n.g", "b-a-n-g-s-a-t", "t   o   l   o   l", "@.n.j.1.n.g"
SPACED_LETTERS_REGEX = re.compile(
    r"(?:^|(?<=\s))(?:[a-zA-Z0-9@$+|][\.\-_/ \t]+){2,}[a-zA-Z0-9@$+|](?=\s|[!?,.]|$)",
    re.IGNORECASE
)

HEX_ESCAPE_REGEX = re.compile(r"(?:\\x[0-9a-fA-F]{2}){2,}")
BASE64_BLOCK_REGEX = re.compile(r"\b[A-Za-z0-9+/]{12,}={0,2}\b")


def strip_invisible_characters(text: str) -> str:
    """
    Removes zero-width, formatting, and invisible unicode characters injected to bypass text filters.
    Includes Unicode category 'Cf' (Format), 'Cc' (Control except newline/tab),
    and normalizes strange separator spaces ('Zs' beyond ASCII space).
    """
    cleaned_chars = []
    for c in text:
        if c in INVISIBLE_CHARS:
            continue
        cat = unicodedata.category(c)
        if cat == "Cf":
            continue
        if cat == "Cc" and c not in ("\n", "\r", "\t"):
            continue
        if cat == "Zs" and c != " ":
            cleaned_chars.append(" ")
            continue
        cleaned_chars.append(c)
    return "".join(cleaned_chars)


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
    Example: 'a.n.j.i.n.g' -> 'anjing', 'b-a-n-g-s-a-t' -> 'bangsat', 't  o  l  o  l' -> 'tolol'
    """
    def _repl(match):
        segment = match.group(0)
        # Strip all punctuation and whitespace between the single characters
        cleaned = re.sub(r"[\.\-_/ \t]+", "", segment)
        return cleaned

    return SPACED_LETTERS_REGEX.sub(_repl, text)


def unpack_encoded_payloads(text: str) -> str:
    """
    Adversarial de-encapsulation: Detects and unrolls Base64 or Hex encoded blocks
    often used to smuggle malicious instructions past perimeter filters directly to LLMs.
    """
    unpacked_fragments = []

    # 1. Unroll hex escape sequences like \x6b\x6f\x6e\x74\x6f\x6c
    def _hex_unpacker(match):
        raw_hex = match.group(0).replace("\\x", "")
        try:
            decoded = bytes.fromhex(raw_hex).decode("utf-8", errors="ignore")
            if decoded.isprintable() and len(decoded.strip()) >= 2:
                unpacked_fragments.append(decoded)
        except Exception:
            pass
        return match.group(0)

    HEX_ESCAPE_REGEX.sub(_hex_unpacker, text)

    # 2. Unroll Base64 blocks (12+ characters)
    for candidate in BASE64_BLOCK_REGEX.findall(text):
        try:
            padded = candidate + "=" * ((4 - len(candidate) % 4) % 4)
            decoded_bytes = base64.b64decode(padded)
            decoded_text = decoded_bytes.decode("utf-8")
            if decoded_text.isprintable() and len(decoded_text.strip()) >= 3:
                if any(c.isalpha() for c in decoded_text):
                    unpacked_fragments.append(decoded_text)
        except Exception:
            continue

    if unpacked_fragments:
        return f"{text} [DECODED_PAYLOAD: {' '.join(unpacked_fragments)}]"
    return text
