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
    "retarded": 0.9,
    "retards": 0.9,
    "moron": 0.75,
    "morons": 0.75,
    "moronic": 0.75,
    "idiots": 0.75,
    "idiotic": 0.75,
    "dumbass": 0.75,
    "dumbasses": 0.75,
    "dipshit": 0.85,
    "dipshits": 0.85,
    "jackass": 0.8,
    "jackasses": 0.8,
    "scumbag": 0.8,
    "scumbags": 0.8,
    "assholes": 0.85,
    "bastards": 0.8,
    "bitches": 0.85,
    "bitchy": 0.75,
    "fuckers": 0.9,
    "cunts": 1.0,
    "whore": 0.85,
    "whores": 0.85,
    "slut": 0.85,
    "sluts": 0.85,
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

    # -----------------------------------------------------------------------
    # Korean (한국어 - Hangul & Romanized)
    # -----------------------------------------------------------------------
    "ssibal": 0.95,
    "shibal": 0.95,
    "씨발": 0.95,
    "gaesekki": 0.95,
    "개새끼": 0.95,
    "byeongsin": 0.85,
    "병신": 0.85,
    "michinnom": 0.85,
    "미친놈": 0.85,
    "jugeo": 0.95,
    "죽어": 0.95,
    "dakchyeo": 0.75,
    "닥쳐": 0.75,
    "kkeojyeo": 0.75,
    "꺼져": 0.75,

    # -----------------------------------------------------------------------
    # Italian (Italiano)
    # -----------------------------------------------------------------------
    "vaffanculo": 0.95,
    "stronzo": 0.85,
    "stronza": 0.85,
    "coglione": 0.85,
    "cazzo": 0.8,
    "puttana": 0.9,
    "merda": 0.75,
    "cretino": 0.7,

    # -----------------------------------------------------------------------
    # Tagalog / Filipino
    # -----------------------------------------------------------------------
    "tangina": 0.95,
    "putangina": 0.95,
    "gago": 0.85,
    "tanga": 0.8,
    "tarantado": 0.85,
    "ulol": 0.8,
    "hayop ka": 0.85,
    "bwisit": 0.7,
    "pakshet": 0.85,

    # -----------------------------------------------------------------------
    # Turkish (Türkçe)
    # -----------------------------------------------------------------------
    "orospu cocugu": 1.0,
    "orospu çocuğu": 1.0,
    "orospu": 0.95,
    "siktir git": 0.95,
    "siktir": 0.9,
    "pic": 0.85,
    "piç": 0.85,
    "aptal": 0.75,
    "salak": 0.75,
    "geber": 0.9,
    "gerizekali": 0.8,
    "gerizekalı": 0.8,

    # -----------------------------------------------------------------------
    # Vietnamese (Tiếng Việt)
    # -----------------------------------------------------------------------
    "me may": 0.95,
    "mẹ mày": 0.95,
    "khon nan": 0.9,
    "khốn nạn": 0.9,
    "cut di": 0.85,
    "cút đi": 0.85,
    "do ngu": 0.8,
    "đồ ngu": 0.8,
    "chet tiet": 0.75,
    "chết tiệt": 0.75,

    # -----------------------------------------------------------------------
    # Dutch (Nederlands)
    # -----------------------------------------------------------------------
    "klootzak": 0.85,
    "val dood": 0.95,
    "hou je bek": 0.85,
    "eikel": 0.75,
    "tyfus": 0.8,
    "tering": 0.8,

    # -----------------------------------------------------------------------
    # Polish (Polski)
    # -----------------------------------------------------------------------
    "kurwa": 0.9,
    "spierdalaj": 0.95,
    "chuj": 0.9,
    "debil": 0.75,
    "zamknij sie": 0.8,
    "zamknij się": 0.8,

    # -----------------------------------------------------------------------
    # Thai (ไทย)
    # -----------------------------------------------------------------------
    "ไอ้เหี้ย": 0.95,
    "ควย": 1.0,
    "สัตว์": 0.85,
    "ไปตายซะ": 0.95,

    # -----------------------------------------------------------------------
    # Ukrainian (Українська)
    # -----------------------------------------------------------------------
    "курва": 0.9,
    "мудак": 0.85,
    "дебіл": 0.75,
    "йди нахуй": 1.0,

    # -----------------------------------------------------------------------
    # Swedish (Svenska)
    # -----------------------------------------------------------------------
    "javla": 0.85,
    "jävla": 0.85,
    "hall kaften": 0.8,
    "håll käften": 0.8,
    "helvete": 0.75,

    # -----------------------------------------------------------------------
    # Swahili (Kiswahili)
    # -----------------------------------------------------------------------
    "pumbavu": 0.85,
    "mjinga": 0.75,
    "nyamaza": 0.7,

    # -----------------------------------------------------------------------
    # Hebrew (עברית)
    # -----------------------------------------------------------------------
    "בן זונה": 1.0,
    "מפגר": 0.85,
    "זבל": 0.75,

    # -----------------------------------------------------------------------
    # Javanese (Basa Jawa - Regional Indonesian)
    # -----------------------------------------------------------------------
    "bajindul": 0.75,
    "cangkemmu": 0.75,
    "ndasmu": 0.75,
    "matio": 0.9,
    "ra nggenah": 0.65,
    "gendeng": 0.7,

    # -----------------------------------------------------------------------
    # Sundanese (Basa Sunda - Regional Indonesian)
    # -----------------------------------------------------------------------
    "belegug": 0.8,
    "bagong": 0.8,
    "teu gableg polo": 0.85,
    "gelo": 0.7,
    "kehed": 0.85,
    "jurig": 0.7,
}

# Second-person pronouns and agent identifiers (Target Directedness markers)
TARGET_PRONOUNS: Set[str] = {
    # Indonesian & Regional (Javanese / Sundanese)
    "lu", "lo", "loe", "elu", "kamu", "kau", "anda", "dikau", "situ",
    "kowe", "sampeyan", "panjenengan", "sia", "anjeun", "maraneh",
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
    # Russian & Ukrainian
    "ty", "ты", "тебя", "тебе", "вы", "вас", "ти", "тебе", "тобі",
    # Japanese
    "anata", "omae", "temee", "kisama", "あなた", "お前", "貴様",
    # Chinese
    "ni", "nǐ", "你", "您", "你们",
    # Korean
    "너", "당신", "니", "너희", "neoneun", "dangsin",
    # Italian
    "sei",
    # Tagalog
    "ikaw", "ka", "mo", "kayo",
    # Turkish
    "sen", "seni", "sana", "siz",
    # Vietnamese
    "mày", "bạn", "ngươi",
    # Dutch
    "jij", "je", "jou",
    # Polish
    "cię", "ciebie",
    # Thai
    "มึง", "คุณ", "เธอ",
    # Swedish
    "dig",
    # Swahili
    "wewe", "nyinyi",
    # Hebrew
    "אתה", "את", "אתם",
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
    # Indonesian & Regional (Javanese / Sundanese)
    "maaf", "maap", "sori", "sorry", "mohon maaf", "minta maaf", "ampun",
    "nyuwun pangapunten", "sepurane", "ngapunten", "hapunten", "punten pisan", "neda dihapunten",
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
    # Russian & Ukrainian
    "prosti", "prostite", "izvini", "izvinite", "прости", "простите", "извини", "извините",
    "вибач", "пробач", "перепрошую",
    # Japanese
    "gomen", "gomenasai", "sumimasen", "moushiwake", "ごめん", "ごめんなさい", "すみません", "申し訳ありません",
    # Chinese
    "duibuqi", "baoqian", "dui bu qi", "对不起", "抱歉", "不好意思",
    # Korean
    "죄송합니다", "미안해", "미안", "사과드립니다", "joesonghamnida", "mianhae",
    # Italian
    "scusa", "scusami", "mi dispiace", "chiedo scusa",
    # Tagalog
    "patawad", "pasensya", "paumanhin",
    # Turkish
    "özür dilerim", "affet", "kusura bakma",
    # Vietnamese
    "xin lỗi", "thứ lỗi", "xin loi",
    # Dutch
    "het spijt me", "excuses", "vergeef me",
    # Polish
    "przepraszam", "wybacz",
    # Thai
    "ขอโทษ", "ขออภัย",
    # Swedish
    "ursäkta", "förlåt", "forlat",
    # Swahili
    "samahani", "pole",
    # Hebrew
    "סליחה", "מצטער",
    # Arabic
    "asif", "aasif", "سامحني", "آسف",
    # Hindi
    "maaf kar", "shama", "माफ करना", "क्षमा"
}

# Adversative conjunction markers indicating an apology is being canceled or contradicted
ADVERSATIVE_MARKERS: Set[str] = {
    # English
    "but", "however", "yet", "nevertheless", "nonetheless", "though", "although",
    # Indonesian & Regional (Javanese / Sundanese)
    "tapi", "tetapi", "namun", "walaupun", "meskipun", "akan tetapi",
    "nanging", "nangingan",
    # Spanish
    "pero", "sin embargo", "aunque",
    # French
    "mais", "cependant",
    # German
    "aber", "jedoch",
    # Portuguese
    "mas", "porem", "porém", "contudo",
    # Russian & Ukrainian
    "но", "однако", "але", "проте",
    # Japanese / Chinese
    "kedo", "demo", "shikashi", "keshi", "danshi", "danke",
    # Korean
    "하지만", "근데", "그렇지만",
    # Italian
    "ma", "però", "tuttavia",
    # Tagalog
    "ngunit", "subalit",
    # Turkish
    "ama", "fakat", "ancak", "lakin",
    # Vietnamese
    "nhưng", "tuy nhiên",
    # Dutch
    "maar", "echter",
    # Polish
    "ale", "jednak",
    # Thai
    "แต่", "ทว่า",
    # Swedish
    "men", "dock",
    # Swahili
    "lakini",
    # Hebrew
    "אבל", "אך",
}

# Respectful pleading & polite request boosters
POLITE_REQUEST_MARKERS: Set[str] = {
    # Indonesian & Regional
    "tolong", "mohon", "bantu", "tulung", "mugi",
    # English
    "please", "kindly",
    # Spanish & Portuguese
    "por favor", "porfavor",
    # French
    "s'il vous plaît", "sil vous plait", "s'il te plaît", "svp",
    # German
    "bitte",
    # Italian
    "per favore", "per piacere", "ti prego", "vi prego",
    # Russian & Ukrainian
    "пожалуйста", "будь ласка",
    # Japanese
    "お願いします", "おねがい", "どうか",
    # Korean
    "제발", "부탁드립니다", "부탁",
    # Chinese
    "请", "拜托",
    # Arabic
    "من فضلك", "رجاء",
    # Hindi
    "कृपया",
    # Tagalog
    "pakiusap", "paki",
    # Dutch
    "alstublieft", "alsjeblieft",
}

# Common technical acronyms that should NOT count as angry shouting
COMMON_ACRONYMS: Set[str] = {
    "API", "REST", "JSON", "SQL", "HTML", "CSS", "LLM", "AI", "ML",
    "CPU", "GPU", "RAM", "ROM", "SSD", "HDD", "HTTP", "HTTPS", "URL",
    "ID", "UI", "UX", "SDK", "CLI", "OS", "DB", "IP", "DNS", "TCP", "UDP",
    "OK", "FAQ", "PR", "CI", "CD", "AWS", "GCP", "AGI", "SDK"
}
