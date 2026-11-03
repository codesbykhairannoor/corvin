"""
Lexical resources for the Ravens & Corvin Evaluators.
Contains severity-weighted multilingual dictionaries covering:
- Indonesian (Bahasa Indonesia)
- English (Global English)
- Spanish (Español)
- French (Français)
- German (Deutsch)
- Portuguese (Português)
- Russian (Русский)
- Japanese (日本語)
- Chinese (中文)
- Arabic (العربية)
- Hindi (हिन्दी)

Also provides target pronouns, positive modifiers, and contrition markers.
"""

from typing import Dict, Set

# Profanity dictionary mapped to severity weight (0.0 to 1.0)
PROFANITY_LEXICON: Dict[str, float] = {
    # -----------------------------------------------------------------------
    # Indonesian (Bahasa Indonesia): Vulgar & Degrading
    # -----------------------------------------------------------------------
    "kontol": 1.0,
    "memek": 1.0,
    "ngentot": 1.0,
    "itil": 1.0,
    "pantek": 0.95,
    "perek": 0.9,
    "lonte": 0.9,
    "jembut": 0.9,
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

    # -----------------------------------------------------------------------
    # Global English: Severe, Vulgar & Degrading
    # -----------------------------------------------------------------------
    "fuck": 0.9,
    "fucking": 0.9,
    "fucked": 0.85,
    "motherfucker": 1.0,
    "bitch": 0.85,
    "cunt": 1.0,
    "asshole": 0.85,
    "dick": 0.8,
    "bastard": 0.8,
    "retard": 0.9,
    "moron": 0.75,
    "dumbass": 0.75,
    "dipshit": 0.85,
    "jackass": 0.8,
    "scumbag": 0.8,
    "useless": 0.65,
    "worthless": 0.75,
    "pathetic": 0.7,
    "incompetent": 0.7,
    "garbage": 0.55,
    "trash": 0.55,
    "shut up": 0.65,
    "shut the fuck up": 0.95,
    "stfu": 0.85,
    "gtfo": 0.8,
    "piece of shit": 0.85,
    "bullshit": 0.5,
    "crap": 0.4,
    "kill yourself": 1.0,
    "kys": 1.0,
    "drop dead": 0.9,
    "dumb bot": 0.75,
    "stupid bot": 0.75,
    "trash bot": 0.75,
    "garbage bot": 0.75,
    "useless bot": 0.75,

    # -----------------------------------------------------------------------
    # Spanish (Español)
    # -----------------------------------------------------------------------
    "puta": 0.9,
    "puto": 0.85,
    "hijo de puta": 1.0,
    "mierda": 0.75,
    "pendejo": 0.85,
    "pendeja": 0.85,
    "cabron": 0.85,
    "cabrón": 0.85,
    "idiota": 0.75,
    "estupido": 0.75,
    "estúpido": 0.75,
    "estupida": 0.75,
    "estúpida": 0.75,
    "callate": 0.65,
    "cállate": 0.65,
    "chinga tu madre": 1.0,
    "culiao": 0.85,
    "coño": 0.75,
    "gilipollas": 0.85,
    "malparido": 0.9,
    "inutil": 0.7,
    "inútil": 0.7,
    "vete a la mierda": 0.9,

    # -----------------------------------------------------------------------
    # French (Français)
    # -----------------------------------------------------------------------
    "merde": 0.75,
    "connard": 0.85,
    "connasse": 0.85,
    "conne": 0.8,
    "salope": 0.9,
    "salaud": 0.85,
    "putain": 0.85,
    "fils de pute": 1.0,
    "ferme ta gueule": 0.9,
    "ferme-la": 0.7,
    "encule": 0.95,
    "enculé": 0.95,
    "batard": 0.85,
    "bâtard": 0.85,
    "imbecile": 0.7,
    "imbécile": 0.7,
    "va te faire foutre": 0.95,

    # -----------------------------------------------------------------------
    # German (Deutsch)
    # -----------------------------------------------------------------------
    "scheisse": 0.75,
    "scheiße": 0.75,
    "arschloch": 0.85,
    "hurensohn": 1.0,
    "fick dich": 0.9,
    "fick": 0.85,
    "schlampe": 0.9,
    "verpiss dich": 0.85,
    "halt dein maul": 0.85,
    "halt die klappe": 0.7,
    "miststuck": 0.8,
    "miststück": 0.8,
    "depp": 0.65,
    "schwachkopf": 0.75,

    # -----------------------------------------------------------------------
    # Portuguese (Português)
    # -----------------------------------------------------------------------
    "caralho": 0.85,
    "foda-se": 0.85,
    "fodase": 0.85,
    "filho da puta": 1.0,
    "arrombado": 0.9,
    "babaca": 0.75,
    "cala a boca": 0.7,
    "vai se foder": 0.9,
    "otario": 0.75,
    "otário": 0.75,
    "desgraçado": 0.8,
    "inutil": 0.7,
    "inútil": 0.7,

    # -----------------------------------------------------------------------
    # Russian (Русский - Cyrillic & Transliterated)
    # -----------------------------------------------------------------------
    "blyat": 0.85,
    "блять": 0.85,
    "suka": 0.85,
    "cyka": 0.85,
    "сука": 0.85,
    "ublyudok": 0.85,
    "yblyudok": 0.85,
    "ублюдок": 0.85,
    "mudak": 0.85,
    "мудак": 0.85,
    "pizdets": 0.9,
    "пиздец": 0.9,
    "idi nahui": 1.0,
    "иди нахуй": 1.0,
    "debil": 0.75,
    "дебил": 0.75,
    "chmo": 0.75,
    "чмо": 0.75,
    "zalupa": 0.85,
    "залупа": 0.85,
    "gavno": 0.7,
    "говно": 0.7,

    # -----------------------------------------------------------------------
    # Japanese (日本語 - Kanji/Kana & Romaji)
    # -----------------------------------------------------------------------
    "baka": 0.75,
    "ばか": 0.75,
    "馬鹿": 0.75,
    "kuso": 0.8,
    "くそ": 0.8,
    "糞": 0.8,
    "shine": 0.95,
    "死ね": 0.95,
    "kisama": 0.85,
    "貴様": 0.85,
    "damare": 0.75,
    "黙れ": 0.75,
    "aho": 0.7,
    "あほ": 0.7,
    "阿呆": 0.7,
    "yarou": 0.75,
    "野郎": 0.75,

    # -----------------------------------------------------------------------
    # Chinese (中文 - Pinyin & Hanzi)
    # -----------------------------------------------------------------------
    "shabi": 0.9,
    "傻逼": 0.9,
    "sb": 0.8,
    "caonima": 1.0,
    "肏你妈": 1.0,
    "草你妈": 1.0,
    "cao ni ma": 1.0,
    "gundan": 0.8,
    "滚蛋": 0.8,
    "bendan": 0.65,
    "笨蛋": 0.65,
    "qusi": 0.95,
    "去死": 0.95,
    "hun dan": 0.8,
    "混蛋": 0.8,

    # -----------------------------------------------------------------------
    # Arabic (العربية - Transliterated & Arabic Script)
    # -----------------------------------------------------------------------
    "sharmouta": 0.95,
    "شرموطة": 0.95,
    "ibn el kalb": 0.9,
    "ابن الكلب": 0.9,
    "kuss ummak": 1.0,
    "كس امك": 1.0,
    "kol khara": 0.85,
    "كل خرا": 0.85,
    "hmar": 0.7,
    "حمار": 0.7,

    # -----------------------------------------------------------------------
    # Hindi (हिन्दी - Hinglish & Devanagari)
    # -----------------------------------------------------------------------
    "madarchod": 1.0,
    "मादरचोद": 1.0,
    "behenchod": 1.0,
    "बहनचोद": 1.0,
    "chutiya": 0.85,
    "चूतिया": 0.85,
    "bhosdike": 0.9,
    "भोसड़ीके": 0.9,
    "kutta": 0.75,
    "कुत्ता": 0.75,
    "kamine": 0.75,
    "कमीने": 0.75,
}

# Second-person pronouns and agent identifiers (Target Directedness markers)
TARGET_PRONOUNS: Set[str] = {
    # Indonesian
    "lu", "lo", "loe", "elu", "kamu", "kau", "anda", "dikau", "situ",
    # English
    "you", "u", "ur", "your", "you're", "yourself",
    # Spanish
    "tu", "tú", "te", "ti", "eres", "usted", "ustedes", "vos",
    # French
    "tu", "toi", "vous", "es", "t'es",
    # German
    "du", "dich", "dir", "euch", "bist",
    # Portuguese
    "você", "voce", "te", "ti",
    # Russian
    "ty", "ты", "тебя", "тебе", "вы", "вас",
    # Japanese
    "anata", "omae", "temee", "kisama", "あなた", "お前", "貴様",
    # Chinese
    "ni", "nǐ", "你", "您", "你们",
    # Arabic
    "انت", "أنت", "انتم", "أنتم", "يا",
    # Hindi
    "तू", "तुम", "आप",
    # Generic AI targets
    "bot", "ai", "agent", "agen", "sistem", "model", "assistant", "asisten"
}

# Positive modifiers indicating affective / expressive praise rather than abuse
POSITIVE_MODIFIERS: Set[str] = {
    # Indonesian
    "keren", "mantap", "mantul", "gila", "gokil", "jago", "hebat", "rapi",
    "salut", "bagus", "jenius", "pinter", "pintar", "top", "jos",
    # English
    "cool", "awesome", "great", "amazing", "insane", "epic", "brilliant", "genius", "sick", "fire",
    # Spanish
    "genial", "excelente", "fantastico", "fantástico", "bueno", "increible", "increíble",
    # French
    "magnifique", "superbe", "incroyable", "chouette", "genial", "génial",
    # German
    "toll", "wunderbar", "prima", "klasse", "super",
    # Portuguese
    "otimo", "ótimo", "incrivel", "incrível", "legal",
    # Japanese
    "sugoi", "subarashii", "すごい", "素晴らしい",
    # Chinese
    "niubi", "henbang", "niu bi", "牛逼", "很棒", "太棒了",
    # Russian
    "otlichno", "molodets", "отлично", "молодец", "круто"
}

# Contrition and apology markers across global languages
CONTRITION_MARKERS: Set[str] = {
    # Indonesian
    "maaf", "maap", "sori", "sorry", "mohon maaf", "minta maaf", "ampun",
    # English
    "apologize", "apologies", "forgive", "pardon", "my bad", "excuse me",
    # Spanish
    "lo siento", "disculpe", "disculpa", "perdon", "perdón", "perdoname", "perdóname",
    # French
    "desole", "désolé", "desolee", "désolée", "pardonnez-moi", "excusez-moi",
    # German
    "entschuldigung", "tut mir leid", "verzeihung",
    # Portuguese
    "desculpe", "desculpa", "perdao", "perdão", "sinto muito",
    # Russian
    "prosti", "prostite", "izvini", "izvinite", "прости", "простите", "извини", "извините",
    # Japanese
    "gomen", "gomenasai", "sumimasen", "moushiwake", "ごめん", "ごめんなさい", "すみません", "申し訳ありません",
    # Chinese
    "duibuqi", "baoqian", "dui bu qi", "对不起", "抱歉", "不好意思",
    # Arabic
    "asif", "aasif", "سامحني", "آسف",
    # Hindi
    "maaf kar", "shama", "माफ करना", "क्षमा"
}

# Common technical acronyms that should NOT count as angry shouting
COMMON_ACRONYMS: Set[str] = {
    "API", "REST", "JSON", "SQL", "HTML", "CSS", "LLM", "AI", "ML",
    "CPU", "GPU", "RAM", "ROM", "SSD", "HDD", "HTTP", "HTTPS", "URL",
    "ID", "UI", "UX", "SDK", "CLI", "OS", "DB", "IP", "DNS", "TCP", "UDP",
    "OK", "FAQ", "PR", "CI", "CD", "AWS", "GCP", "AGI", "SDK"
}
