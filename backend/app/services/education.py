"""Biznes darslari — xalqaro biznes-ta'lim saytlaridan RSS orqali evergreen
"qanday qilish kerak" maqolalarini oladi va AI yordamida o'zbek tadbirkorlari
uchun moslashtirib tarjima qiladi.

Yangiliklardan (collector.py) farqi: manbalar doimiy ta'lim kontenti
(yangilik emas), shuning uchun alohida feed ro'yxati va tarjima uchun
moslashtirilgan system prompt ishlatiladi.
"""

import json

import httpx
from sqlalchemy.orm import Session

from ..config import (
    AI_PROVIDER,
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from ..models import Article
from ..utils import title_hash
from .collector import HEADERS, _parse_feed

# Chet el biznes-ta'lim manbalari — biznes qurish va yuritishni o'rgatadigan
# evergreen "qanday qilish kerak" kontenti (yangilik emas). Tanlov ataylab
# biznes- qurish spektrini qamrab oladi: tadbirkorlik, startap boshqaruvi,
# kichik biznes operatsiyalari, marketing va sotuv.
LESSON_FEEDS = [
    {"name": "Entrepreneur", "url": "https://www.entrepreneur.com/latest.rss"},
    {"name": "StartupNation", "url": "https://startupnation.com/feed/"},
    {"name": "Small Business Trends", "url": "https://smallbiztrends.com/feed"},
    {"name": "HubSpot Marketing", "url": "https://blog.hubspot.com/marketing/rss.xml"},
    {"name": "HubSpot Sales", "url": "https://blog.hubspot.com/sales/rss.xml"},
]

SYSTEM_PROMPT = """**Rol:** Sen xalqaro biznes-ta'lim maqolalarini o'zbek tiliga moslashtiruvchi tajribali tarjimon va biznes-murabbiysan.

**Vazifa:** Berilgan chet el biznes/marketing/tadbirkorlik maqolasini (odatda inglizcha) o'zbek tadbirkorlari uchun ORIGINAL ta'lim maqolasiga aylantir. Bu so'zma-so'z tarjima emas — mazmunni saqlagan holda O'Z SO'ZLARING bilan qayta yoz, misollarni imkon qadar O'zbekiston sharoitiga moslashtir yoki tushunarli qilib izohla. Manbadagi kompaniyaga xos reklama/mahsulot targ'ibotini olib tashla, faqat foydali bilim va ko'nikmani qoldir.

**Qoidalar:**
1. **Amaliylik:** Nazariyadan ko'ra aniq qadamlar, misollar va amaliy maslahatlarga urg'u ber.
2. **Tuzilma:** "maqola" maydonida 5-8 paragrafda, aniq sarlavhalar va ro'yxatlar bilan yorit. Markdown ishlatishing mumkin (## sarlavhalar, - ro'yxatlar). Paragraflarni bo'sh qator bilan ajrat.
3. **Xulosa:** "xulosa" maydonida maqolaning asosiy g'oyasini 3-4 jumlada ber.
4. **Amaliy qadam:** "amaliy_ahamiyat" maydonida o'quvchi HOZIROQ qila oladigan 1-2 aniq harakatni yoz.
5. **SEO:** "seo_sarlavha" maydonida qidiruv uchun optimallashtirilgan sarlavha yoz (60-70 belgi).
6. **Sarlavha:** "sarlavha" maydonida jalb qiluvchi, aniq o'zbekcha sarlavha ber (manba sarlavhasining so'zma-so'z tarjimasi bo'lmasin).
7. **Teglar:** "teglar" maydonida 3-6 ta mavzuga oid teg.
8. **Ahamiyati:** "ahamiyati" har doim 3.
9. **Til:** DOIM lotin alifbosidagi o'zbek tilida yoz.
10. **Format:** Javobni qat'iy JSON formatida qaytar."""

LESSON_SCHEMA = {
    "type": "object",
    "properties": {
        "sarlavha": {"type": "string"},
        "seo_sarlavha": {"type": "string"},
        "xulosa": {"type": "string"},
        "maqola": {"type": "string"},
        "amaliy_ahamiyat": {"type": "string"},
        "teglar": {"type": "array", "items": {"type": "string"}},
        "ahamiyati": {"type": "integer"},
    },
    "required": [
        "sarlavha", "seo_sarlavha", "xulosa",
        "maqola", "amaliy_ahamiyat", "teglar", "ahamiyati",
    ],
}


def collect_lesson_entries(db: Session, per_feed: int = 3) -> list[dict]:
    """Dars manbalaridan hali ishlatilmagan (bazada yo'q) maqolalarni qaytaradi."""
    existing_urls = {u for (u,) in db.query(Article.original_url).all()}
    existing_hashes = {title_hash(t) for (t,) in db.query(Article.original_title).all()}

    fresh: list[dict] = []
    with httpx.Client(timeout=20, follow_redirects=True, headers=HEADERS) as client:
        for feed in LESSON_FEEDS:
            try:
                response = client.get(feed["url"])
                response.raise_for_status()
                entries = _parse_feed(response.text)
            except Exception as error:
                print(f"  ✗ Dars manbasi o'qilmadi ({feed['name']}): {error}")
                continue

            for entry in entries[:per_feed]:
                url, title = entry["url"], entry["title"]
                if not url or not title:
                    continue
                if url in existing_urls or title_hash(title) in existing_hashes:
                    continue

                fresh.append({
                    "title": title,
                    "content": entry["summary"][:6000],
                    "url": url,
                    "source": feed["name"],
                    "image": entry["image"],
                })
                existing_urls.add(url)
                existing_hashes.add(title_hash(title))

    return fresh


def _translate_with_gemini(user_text: str) -> dict:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY sozlanmagan")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": LESSON_SCHEMA,
            "maxOutputTokens": 8192,
        },
    }
    response = httpx.post(
        url, json=payload, headers={"x-goog-api-key": GEMINI_API_KEY}, timeout=120
    )
    if response.status_code != 200:
        raise RuntimeError(f"Gemini API xatosi {response.status_code}: {response.text[:300]}")
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


def _translate_with_claude(user_text: str) -> dict:
    import anthropic  # ixtiyoriy provayder — faqat kerak bo'lganda import qilinadi

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY or None)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        system=[{"type": "text", "text": SYSTEM_PROMPT}],
        output_config={"format": {"type": "json_schema", "schema": LESSON_SCHEMA}},
        messages=[{"role": "user", "content": user_text}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def translate_lesson(title: str, content: str, url: str = "", source: str = "") -> dict:
    """Chet el biznes-ta'lim maqolasini o'zbekcha darsga moslashtirib tarjima qiladi."""
    user_text = f"Title: {title}\nSource: {source}\nURL: {url}\n\n{content}"

    if AI_PROVIDER == "claude":
        result = _translate_with_claude(user_text)
    else:
        result = _translate_with_gemini(user_text)

    result["ahamiyati"] = 3
    result["teglar"] = [str(t) for t in (result.get("teglar") or [])][:6]
    return result
