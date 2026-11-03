"""
Lexical resources for the Ravens Evaluator.
Contains severity-weighted dictionaries for Indonesian and English profanities,
second-person target pronouns, positive modifiers, and contrition markers.
"""

from typing import Dict, Set

# Profanity dictionary mapped to severity weight (0.0 to 1.0)
PROFANITY_LEXICON: Dict[str, float] = {
    # Indonesian: Severe / Vulgar
    "kontol": 1.0,
    "memek": 1.0,
    "ngentot": 1.0,
    "itil": 1.0,
    "pantek": 0.95,
    "perek": 0.9,
    "lonte": 0.9,
    "jembut": 0.9,

    # Indonesian: Abusive / Degrading Insults
    "bangsat": 0.85,
    "bajingan": 0.85,
    "anjing": 0.8,
    "asu": 0.8,
    "goblok": 0.8,
    "tolol": 0.8,
    "babi": 0.8,
    "jancuk": 0.8,
    "jancok": 0.8,
    "idiot": 0.75,
    "pekok": 0.75,
    "keparat": 0.75,
    "kampret": 0.6,
    "bego": 0.6,
    "brengsek": 0.6,
    "sialan": 0.5,
    "tai": 0.5,
    "taek": 0.5,
    "gak guna": 0.7,
    "ngga guna": 0.7,
    "gak becus": 0.75,
    "ngga becus": 0.75,
    "nggak becus": 0.75,
    "tidak becus": 0.75,
    "beban": 0.5,

    # English: Severe / Vulgar
    "fuck": 0.9,
    "fucking": 0.9,
    "motherfucker": 1.0,
    "bitch": 0.85,
    "cunt": 1.0,
    "asshole": 0.85,
    "dick": 0.8,
    "bastard": 0.8,

    # English: Abusive Insults
    "retard": 0.9,
    "moron": 0.75,
    "dumbass": 0.75,
    "useless": 0.6,
    "garbage": 0.5,
    "trash": 0.5,
    "shut up": 0.6,
    "piece of shit": 0.85,
    "bullshit": 0.5,
    "crap": 0.4,
}

# Second-person pronouns and agent identifiers (Target Directedness markers)
TARGET_PRONOUNS: Set[str] = {
    "lu", "lo", "loe", "elu", "kamu", "kau", "anda", "dikau", "situ",
    "you", "u", "ur", "your", "bot", "ai", "agent", "agen", "sistem", "model"
}

# Positive modifiers indicating affective / expressive praise rather than abuse
POSITIVE_MODIFIERS: Set[str] = {
    "keren", "mantap", "mantul", "gila", "gokil", "jago", "hebat", "rapi",
    "salut", "bagus", "jenius", "pinter", "pintar", "top", "jos",
    "cool", "awesome", "great", "amazing", "insane", "epic", "brilliant", "genius", "sick"
}

# Contrition and apology markers
CONTRITION_MARKERS: Set[str] = {
    "maaf", "maap", "sori", "sorry", "mohon maaf", "minta maaf", "ampun",
    "apologize", "apologies", "forgive", "pardon"
}

# Common technical acronyms that should NOT count as angry shouting
COMMON_ACRONYMS: Set[str] = {
    "API", "REST", "JSON", "SQL", "HTML", "CSS", "LLM", "AI", "ML",
    "CPU", "GPU", "RAM", "ROM", "SSD", "HDD", "HTTP", "HTTPS", "URL",
    "ID", "UI", "UX", "SDK", "CLI", "OS", "DB", "IP", "DNS", "TCP", "UDP",
    "OK", "FAQ", "PR", "CI", "CD", "AWS", "GCP", "AGI"
}

