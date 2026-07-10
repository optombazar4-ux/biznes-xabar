import hashlib
import re


def slugify(text: str) -> str:
    """O'zbek lotin matnidan URL uchun slug yasaydi."""
    text = text.lower().replace("'", "").replace("ʻ", "").replace("’", "")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:200] or "maqola"


def title_hash(title: str) -> str:
    """Dublikatlarni aniqlash uchun normallashtirilgan sarlavha xeshi."""
    normalized = re.sub(r"[^a-z0-9]", "", title.lower())
    return hashlib.sha256(normalized.encode()).hexdigest()


# Sarlavhalarda ma'no tashimaydigan keng tarqalgan so'zlar (asosan inglizcha —
# manbalar inglizcha, dublikat tekshiruvi AI tarjimasidan oldin bo'ladi).
_TITLE_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "for", "to", "of", "in", "on", "at",
    "by", "with", "from", "as", "is", "are", "was", "were", "be", "been", "this",
    "that", "these", "those", "it", "its", "his", "her", "their", "you", "your",
    "we", "our", "how", "why", "what", "when", "who", "new", "now", "will",
    "can", "not", "no", "yes", "he", "she", "they", "has", "have", "had",
    "here", "out", "up", "down", "off", "over", "into", "than", "then", "just",
    "about", "after", "before", "more", "most", "some", "all", "one", "two",
    "get", "got", "make", "made", "way", "ways", "top", "best", "your", "vs",
}


def title_tokens(title: str) -> set[str]:
    """Sarlavhani ma'noli so'zlar to'plamiga aylantiradi (dublikat tekshiruvi uchun).

    So'zlar 2 harfdan uzun bo'lishi kerak; raqamlar (sana, foiz, summa —
    yangiliklarda kuchli dublikat signali) 2 xonadan boshlab saqlanadi.
    """
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


def is_near_duplicate(tokens: set[str], seen: list[set[str]], threshold: float = 0.5) -> bool:
    """tokens 'seen' ichidagi biror sarlavha bilan yetarlicha o'xshasa True.

    O'xshashlik = kesishma / kichikroq to'plam (overlap koeffitsienti) — turli
    uzunlikdagi sarlavhalar uchun Jaccard'dan barqarorroq. Bir voqeani turli
    manbalar yozganda kompaniya nomlari, raqamlar va kalit so'zlar bir xil bo'ladi.
    Chegara 0.5: kuzatilgan ma'lumotda turli voqealar <=0.25, bir voqea variantlari
    >=0.57 — bu oraliqda toza ajraladi.
    """
    if len(tokens) < 3:
        return False  # juda qisqa sarlavha — ishonchsiz, o'tkazib yuboramiz
    for other in seen:
        if len(other) < 3:
            continue
        overlap = len(tokens & other)
        if overlap and overlap / min(len(tokens), len(other)) >= threshold:
            return True
    return False
