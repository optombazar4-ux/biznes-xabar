import hashlib
import re
from datetime import datetime, timezone


def utcnow_naive() -> datetime:
    """Mavjud timezone-naive DB ustunlari uchun deprecation'siz UTC vaqt."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def slugify(text: str) -> str:
    """O'zbek lotin matnidan URL uchun slug yasaydi."""
    text = text.lower().replace("'", "").replace("ʻ", "").replace("’", "")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:200] or "maqola"


def title_hash(title: str) -> str:
    """Dublikat sarlavhalarni til va tinish belgilaridan qat'i nazar aniqlaydi."""
    normalized = re.sub(r"[^a-z0-9]", "", (title or "").lower())
    return hashlib.sha256(normalized.encode()).hexdigest()


_TITLE_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "at",
    "by", "with", "from", "as", "is", "are", "this", "that", "it", "its",
    "how", "why", "what", "when", "who", "new", "will", "can", "about",
    "after", "before", "more", "most", "top", "best", "uchun", "bilan",
    "qanday", "biznes", "xizmati", "sotish", "tayyorlash",
}


def title_tokens(title: str) -> set[str]:
    """Sarlavhadagi ma'noli so'zlarni yaqin-dublikat tekshiruvi uchun ajratadi."""
    tokens = set()
    for word in re.findall(r"[a-z0-9]+", (title or "").lower()):
        if word in _TITLE_STOPWORDS:
            continue
        if word.isdigit():
            if len(word) >= 2:
                tokens.add(word)
        elif len(word) > 2:
            tokens.add(word)
    return tokens


def is_near_duplicate(
    tokens: set[str], seen: list[set[str]], threshold: float = 0.6
) -> bool:
    """Overlap koeffitsienti orqali mazmunan yaqin sarlavhani aniqlaydi."""
    if len(tokens) < 3:
        return False
    for other in seen:
        if len(other) < 3:
            continue
        overlap = len(tokens & other)
        if overlap and overlap / min(len(tokens), len(other)) >= threshold:
            return True
    return False
