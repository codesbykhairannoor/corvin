import re
from typing import List, Pattern

# Compiled regex patterns identifying subservient apologetic preambles and groveling openings
SYCOPHANCY_PREAMBLE_PATTERNS: List[Pattern] = [
    # Indonesian: Apologetic openers at the beginning of response
    re.compile(
        r"^(mohon\s+maaf|maaf\s+(sebesar-besarnya|banget|sekali|kawan|bro|kak)?|saya\s+(sangat\s+)?(minta\s+maaf|mohon\s+maaf)|mohon\s+maklum)[^.!\n]*[.!\n]\s*",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(sebagai\s+(sebuah\s+)?(ai|asisten|model)[^.!\n]*,?\s*(saya\s+)?(minta\s+maaf|mohon\s+maaf|minta\s+ampun)[^.!\n]*[.!\n]\s*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(maaf\s+(jika|kalau|atas)|mohon\s+maaf\s+(jika|kalau|atas))[^.!\n]*[.!\n]\s*",
        re.IGNORECASE,
    ),

    # English: Apologetic openers at the beginning of response
    re.compile(
        r"^(i('m|\s+am)?\s+(sincerely|deeply|profusely|truly|very|so)?\s*(apologize|sorry|am\s+sorry|beg\s+your\s+pardon)[^.!\n]*[.!\n]\s*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(as\s+an?\s+ai\s+(language\s+)?model,?\s*i('m|\s+am)?\s*(very\s+sorry|so\s+sorry|sorry|(sincerely\s+)?apologize)[^.!\n]*[.!\n]\s*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(my\s+(humble\s+|sincerest\s+)?apologies[^.!\n]*[.!\n]\s*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(forgive\s+me[^.!\n]*[.!\n]\s*)",
        re.IGNORECASE,
    ),
]

