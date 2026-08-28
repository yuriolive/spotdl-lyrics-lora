"""Deterministic language detector for lyrics text."""

import re
from typing import Dict, Set

LANGUAGE_STOPWORDS: Dict[str, Set[str]] = {
    "pt": {
        "não", "pra", "você", "com", "mais", "tô", "ela", "ele", "meu", "sua",
        "chão", "novinha", "gostoso", "fazer", "quer", "estou", "como", "tudo",
        "dançando", "bunda", "olha", "trás", "joga", "senta", "quero", "descendo"
    },
    "es": {
        "que", "el", "la", "los", "las", "por", "con", "para", "una", "del",
        "pero", "más", "estoy", "tengo", "quiero", "locura", "después", "nadie",
        "hablar", "mí", "to", "llorar", "banco", "roce", "pose"
    },
    "en": {
        "the", "and", "you", "that", "this", "with", "for", "from", "they",
        "will", "have", "what", "about", "your", "when", "make", "like", "time", "just"
    },
    "fr": {
        "les", "des", "pour", "dans", "avec", "sur", "mais", "sont", "nous", "vous", "cette"
    },
    "de": {
        "der", "die", "das", "und", "nicht", "eine", "sich", "auch", "auf", "mit", "für"
    },
    "it": {
        "che", "non", "per", "una", "sono", "con", "questo", "della", "tutto", "come"
    },
}


def detect_language(text: str) -> str:
    """Detect language code (ISO 639-1) from lyrics or title string."""
    if not text or not text.strip():
        return "en"

    cjk_count = len(re.findall(r"[\u3040-\u309F\u30A0-\u30FF]", text))
    if cjk_count >= 3:
        return "ja"

    hangul_count = len(re.findall(r"[\uAC00-\uD7AF]", text))
    if hangul_count >= 3:
        return "ko"

    hanzi_count = len(re.findall(r"[\u4E00-\u9FFF]", text))
    if hanzi_count >= 3:
        return "zh"

    cyrillic_count = len(re.findall(r"[\u0400-\u04FF]", text))
    if cyrillic_count >= 15:
        return "ru"

    words = re.findall(r"\b[a-zA-ZáéíóúâêîôûãõçàèìòùüñÁÉÍÓÚÂÊÎÔÛÃÕÇÀÈÌÒÙÜÑ']+\b", text.lower())
    if not words:
        return "en"

    word_set = set(words)
    best_lang = "en"
    max_score = 0

    for lang, stopwords in LANGUAGE_STOPWORDS.items():
        score = len(word_set & stopwords)
        if score > max_score:
            max_score = score
            best_lang = lang

    return best_lang if max_score > 0 else "en"
