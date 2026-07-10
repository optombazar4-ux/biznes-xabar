import re


def slugify(text: str) -> str:
    """O'zbek lotin matnidan URL uchun slug yasaydi."""
    text = text.lower().replace("'", "").replace("ʻ", "").replace("’", "")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:200] or "maqola"
