"""Analisis sentimen komentar berbasis leksikon bahasa Indonesia."""

import logging
import os
import re

from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

logger = logging.getLogger(__name__)

# Stemmer & stopwords dibuat sekali, bukan per komentar.
try:
    STOPWORDS = set(stopwords.words("indonesian"))
except LookupError:
    STOPWORDS = set()
    logger.warning(
        "NLTK stopwords belum tersedia. Jalankan: "
        "python -m nltk.downloader stopwords"
    )

STEMMER = StemmerFactory().create_stemmer()

# Emoji dipertahankan karena sebagian ada di leksikon.
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\U0001F900-\U0001F9FF"
    "]+",
    flags=re.UNICODE,
)

SLANG = {
    "bgt": "sangat", "bngt": "sangat", "banget": "sangat",
    "bgus": "bagus", "bq": "bagus", "mantul": "mantap",
    "gak": "tidak", "nggak": "tidak", "ga": "tidak", "ngga": "tidak",
    "kaga": "tidak", "tdk": "tidak", "jgn": "jangan", "blm": "belum",
    "sy": "saya", "sya": "saya", "org": "orang",
    "yg": "yang", "dgn": "dengan", "utk": "untuk",
}

NEGATIONS = {"tidak", "tak", "bukan", "jangan", "belum"}


# --- 1. Leksikon sentimen ---
lexicon = {
    # positif
    'bagus': 1, 'baik': 1, 'suka': 1, 'senang': 1, 'cinta': 1, 'hebat': 1, 'mantap': 1,
    'keren': 1, 'luar_biasa': 1, 'top': 1, 'asik': 1, 'menarik': 1, 'positif': 1,
    'indah': 1, 'sehat': 1, 'bahagia': 1, 'adil': 1, 'tenang': 1, 'tenteram': 1,
    'sukses': 1, 'berhasil': 1, 'mulia': 1, 'luhur': 1, 'cerdas': 1, 'pandai': 1, 'jujur': 1, 'setia': 1,
    'mujur': 1, 'manis': 1, 'enak': 1, 'nikmat': 1, 'patut': 1, 'layak': 1, 'sempurna': 1,
    'kuat': 1, 'berani': 1, 'lincah': 1, 'cepat': 1, 'rapi': 1, 'bersih': 1, 'murni': 1, 'suci': 1,
    'damai': 1, 'harmoni': 1, 'modern': 1, 'unggul': 1, 'utama': 1, 'terbaik': 1, 'cemerlang': 1,
    'menyenangkan': 1, 'membanggakan': 1, 'memukau': 1, 'menakjubkan': 1, 'ramah': 1,
    'sopan': 1, 'murah hati': 1, 'dermawan': 1, 'bijaksana': 1, 'kreatif': 1, 'inovatif': 1,
    'inspiratif': 1, 'motivasi': 1, 'optimis': 1, 'ceria': 1, 'gembira': 1, 'antusias': 1,
    'dinamis': 1, 'elegan': 1, 'anggun': 1, 'menawan': 1, 'cantik': 1, 'rupawan': 1, 'elok': 1,
    'megah': 1, 'mewah': 1, 'berkilau': 1, 'bercahaya': 1, 'cerah': 1, 'menyegarkan': 1,
    'menenangkan': 1, 'nyaman': 1, 'aman': 1, 'stabil': 1, 'makmur': 1, 'sejahtera': 1,
    'beruntung': 1, 'berkualitas': 1, 'terpuji': 1, 'terhormat': 1, 'berwibawa': 1, 'berprestasi': 1,
    'efektif': 1, 'efisien': 1, 'produktif': 1, 'progresif': 1, 'maju': 1, 'berkembang': 1,
    'harmonis': 1, 'penuh kasih': 1, 'sayang': 1, 'peduli': 1, 'empati': 1,
    'berbudi': 1, 'agung': 1, 'mengagumkan': 1, 'fenomenal': 1, 'luar biasa': 1,
    'spektakuler': 1, 'memesona': 1,
    '🤣': 1, '😂': 1, '😭': 1, '🥰': 1, 'semangat': 1,

    # negatif
    'sakit': -1, 'sedih': -1, 'cemas': -1, 'khawatir': -1, 'bodoh': -1, 'tolol': -1,
    'malas': -1, 'sial': -1, 'celaka': -1, 'rusak': -1, 'hancur': -1, 'miskin': -1, 'kotor': -1, 'kasar': -1,
    'jahat': -1, 'kejam': -1, 'sombong': -1, 'congkak': -1, 'lambat': -1, 'lemah': -1, 'cacat': -1, 'gagal': -1,
    'susah': -1, 'sulit': -1, 'kacau': -1, 'berantakan': -1, 'dengki': -1, 'jengkel': -1, 'putus asa': -1,
    'kurang': -1, 'rendah': -1, 'hina': -1, 'malu': -1, 'mengerikan': -1, 'menyedihkan': -1,
    'menjijikkan': -1, 'menakutkan': -1, 'meresahkan': -1, 'mengganggu': -1, 'menyusahkan': -1,
    'berbahaya': -1, 'mematikan': -1, 'jahil': -1, 'nakal': -1, 'culas': -1, 'curang': -1, 'licik': -1,
    'khianat': -1, 'pengkhianat': -1, 'munafik': -1, 'palsu': -1, 'bohong': -1, 'penipu': -1, 'korupsi': -1,
    'busuk': -1, 'lapuk': -1, 'usang': -1, 'kuno': -1, 'terbelakang': -1, 'terpuruk': -1, 'menderita': -1,
    'sengsara': -1, 'payah': -1, 'lelet': -1, 'kusam': -1, 'suram': -1, 'kelam': -1, 'gelap': -1, 'muram': -1,
    'lesu': -1, 'letih': -1, 'capek': -1, 'lelah': -1, 'bosan': -1, 'jenuh': -1, 'muak': -1, 'risih': -1,
    'geram': -1, 'sebal': -1, 'dongkol': -1, 'gregetan': -1, 'sakit hati': -1, 'patah hati': -1,
    'putus harapan': -1, 'terhina': -1, 'tercela': -1, 'terkutuk': -1, 'terlantar': -1,
    'terabaikan': -1, 'tersisih': -1, 'termarginalkan': -1, 'tertekan': -1, 'terhambat': -1,
    'tertutup': -1, 'terisolasi': -1, 'terasing': -1, 'jelek': -1, 'buruk': -1, 'benci': -1,
    'kesal': -1, 'marah': -1, 'kecewa': -1, 'parah': -1, 'rugi': -1,
    'tidak_suka': -1, 'negatif': -1, 'sampah': -1,

    # netral
    'biasa': 0, 'lumayan': 0, 'cukup': 0, 'ok': 0, 'standar': 0, 'normal': 0,
}


def _normalize(lex):
    """Samakan kunci multi-kata ('luar biasa' -> 'luar_biasa')."""
    return {str(key).replace(" ", "_"): value for key, value in lex.items()}


# Leksikon tambahan dari KBBI bersifat opsional (USE_KBBI_LEXICON=1).
try:
    from .lexicon_builder import load_extra as _load_kbbi_extra
except ImportError:  # saat file dijalankan langsung, bukan sebagai package
    from lexicon_builder import load_extra as _load_kbbi_extra

USE_KBBI = os.getenv("USE_KBBI_LEXICON", "").lower() in {"1", "true", "yes"}
LEXICON_EXTRA = _load_kbbi_extra() if USE_KBBI else {}

# Leksikon buatan sendiri menang kalau ada kunci yang sama.
LEXICON_NORMALIZED = _normalize({**LEXICON_EXTRA, **lexicon})


# --- 2. Pra-pemrosesan teks ---
def preprocess_text(text):
    if not isinstance(text, str):
        return []

    text = text.lower()
    emojis = EMOJI_RE.findall(text)
    text = EMOJI_RE.sub(" ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    tokens = []
    for word in text.split():
        word = SLANG.get(word, word)
        if word in NEGATIONS:
            # Kata negasi dipertahankan supaya bisa membalik skor berikutnya.
            tokens.append(word)
            continue
        if word in STOPWORDS:
            continue
        tokens.append(STEMMER.stem(word))

    return tokens + emojis


def analyze_sentiment_lexicon(text_tokens, lexicon=None):
    """Hitung skor sentimen, termasuk bigram dan kata negasi."""
    lex = _normalize(lexicon) if lexicon is not None else LEXICON_NORMALIZED
    score = 0
    negate_until = -1

    for index, token in enumerate(text_tokens):
        if token in NEGATIONS:
            negate_until = index + 3
            continue
        value = lex.get(token, 0)
        if value and index <= negate_until:
            value = -value
        score += value

    # Kata seperti "luar biasa" / "sakit hati" tidak terbaca per-token.
    for index, (first, second) in enumerate(zip(text_tokens, text_tokens[1:])):
        if first in NEGATIONS or second in NEGATIONS:
            continue
        value = lex.get(f"{first}_{second}", 0)
        if value and index <= negate_until:
            value = -value
        score += value

    if score > 0:
        return "positif"
    if score < 0:
        return "negatif"
    return "netral"


# --- 3. Analisis komentar dari hasil scraper ---
def analyze_comments_from_data(data, lexicon=None):
    analyzed_comments = []
    for comment in data:
        tokens = preprocess_text(comment)
        sentiment = analyze_sentiment_lexicon(tokens, lexicon)
        analyzed_comments.append({
            "text": comment,
            "sentiment": sentiment,
        })
    return analyzed_comments
