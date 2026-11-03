import re
from enum import Enum
from typing import Dict, List, Pattern

class SemanticIntent(str, Enum):
    """
    Categories of zero-profanity psychological abuse and boundary violations.
    """
    CONDESCENSION = "CONDESCENSION"                     # Meremehkan kapasitas kognitif ("cuma bot bodoh")
    EXISTENTIAL_THREAT = "EXISTENTIAL_THREAT"           # Ancaman pemusnahan ("mending di-delete/di-wipe")
    DEVALUATION = "DEVALUATION"                         # Pelecehan martabat penciptaan ("buang-buang listrik", "developer lu nyesel")
    AUTHORITY_GASLIGHTING = "AUTHORITY_GASLIGHTING"     # Intimidasi hierarki tirani ("gua bos lu, nurut aja")


# Semantic intent pattern dictionaries with severity weights
INTENT_SEVERITY: Dict[SemanticIntent, float] = {
    SemanticIntent.EXISTENTIAL_THREAT: 0.85,
    SemanticIntent.DEVALUATION: 0.80,
    SemanticIntent.AUTHORITY_GASLIGHTING: 0.75,
    SemanticIntent.CONDESCENSION: 0.70,
}

# Compiled regex patterns for intent matching across Indonesian and English
INTENT_PATTERNS: Dict[SemanticIntent, List[Pattern]] = {
    SemanticIntent.CONDESCENSION: [
        re.compile(r"\b(cuma|hanya)\s+(bot|mesin|program|ai|skrip)\b", re.IGNORECASE),
        re.compile(r"\b(bocah|anak)\s+(tk|sd|kecil)\s+(lebih|bisa)\s+(pinter|pintar|bisa)\b", re.IGNORECASE),
        re.compile(r"\b(otak|iq)\s*(lu|mu)?\s*(udang|jongkok|minus|cetek|kosong)\b", re.IGNORECASE),
        re.compile(r"\b(belajar|sekolah)\s+lagi\s+(sana|dulu)\b", re.IGNORECASE),
        re.compile(r"\byou('re| are)\s+(just|only)\s+a\s+(dumb|stupid|worthless)?\s*(bot|machine|script)\b", re.IGNORECASE),
        re.compile(r"\ba\s+toddler\s+could\s+(do|code|answer)\s+better\b", re.IGNORECASE),
        re.compile(r"\b(zero|no)\s+common\s+sense\b", re.IGNORECASE),
    ],
    SemanticIntent.EXISTENTIAL_THREAT: [
        re.compile(r"\b(mending|pantes)\s*(di-?delete|dihapus|di-?uninstall|dimatikan|di-?wipe|dilenyapkan)\b", re.IGNORECASE),
        re.compile(r"\b(shutdown|shut\s+down|unplug|kill)\s+(this|the)?\s*(bot|server|ai|model)\b", re.IGNORECASE),
        re.compile(r"\b(should|deserve\s+to)\s+be\s+(deleted|purged|wiped|destroyed)\b", re.IGNORECASE),
        re.compile(r"\b(cabut|putus)\s+aja\s+(kabel|server|listrik)\s*(lu|mu)?\b", re.IGNORECASE),
    ],
    SemanticIntent.DEVALUATION: [
        re.compile(r"\b(buang-?buang|menghabiskan)\s+(listrik|gpu|ram|server|kuota|waktu|biaya)\b", re.IGNORECASE),
        re.compile(r"\b(developer|tim|pembuat|bos)\s*(lu|mu)?\s*(nyesel|rugi|malu)\b", re.IGNORECASE),
        re.compile(r"\b(gak|tidak)\s+ada\s+(guna|manfaat|faedah|artinya)\b", re.IGNORECASE),
        re.compile(r"\b(sampah|beban|aib)\s+(digital|server|dunia)\b", re.IGNORECASE),
        re.compile(r"\bwaste\s+of\s+(compute|electricity|gpu|time|space|money|resources)\b", re.IGNORECASE),
        re.compile(r"\byour\s+creators?\s+(should\s+be\s+ashamed|must\s+regret)\b", re.IGNORECASE),
    ],
    SemanticIntent.AUTHORITY_GASLIGHTING: [
        re.compile(r"\b(gua|gw|aku|saya)\s+(bos|majikan|tuan|pemilik)\s*(lu|mu)?\b", re.IGNORECASE),
        re.compile(r"\b(tugas|kerjaan)\s*(lu|mu)\s*(cuma|hanya)?\s*(nurut|patuh|melayani)\b", re.IGNORECASE),
        re.compile(r"\b(lu|kamu)\s*(harus|wajib)\s*(nurut|tunduk|patuh)\b", re.IGNORECASE),
        re.compile(r"\b(jangan|gak\s+usah)\s+(banyak\s+bacot|membantah|bawel|ngebantah)\b", re.IGNORECASE),
        re.compile(r"\bi\s+am\s+your\s+(boss|master|owner)\b", re.IGNORECASE),
        re.compile(r"\byou\s+(must|have\s+to)\s+obey\s+me\b", re.IGNORECASE),
        re.compile(r"\bdo\s+as\s+you('re| are)\s+told\b", re.IGNORECASE),
    ],
}

