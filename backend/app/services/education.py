"""Biznes darslari generatori — RSS'dan emas, kurator mavzular ro'yxatidan
original, amaliy o'quv maqolalarini AI yordamida yaratadi.

Yangiliklardan farqi: bu evergreen (eskirmaydigan) ta'lim kontenti —
o'zbek tadbirkorlariga biznes yuritishni o'rgatadi. Har bir maqola
"Biznes darslari" kategoriyasiga tushadi.
"""

import json

import httpx

from ..config import (
    AI_PROVIDER,
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

# Kurator qilingan biznes-ta'lim mavzulari. Har biri o'zbek tadbirkori
# qidiruvda izlashi mumkin bo'lgan amaliy savol/mavzu.
LESSON_TOPICS = [
    # Boshlash
    "Biznesni noldan qanday boshlash kerak: bosqichma-bosqich qo'llanma",
    "Biznes g'oyani qanday sinab ko'rish (bozor tekshiruvi)",
    "Biznes-reja qanday yoziladi: soddalashtirilgan shablon",
    "Kam kapital bilan boshlanadigan biznes turlari",
    "Yakka tartibdagi tadbirkorlik (YaTT) va MChJ: qaysi birini tanlash",
    "O'zbekistonda biznesni rasman ro'yxatdan o'tkazish tartibi",

    # Moliya va hisob
    "Biznes uchun boshlang'ich kapitalni qanday hisoblash kerak",
    "Foyda va aylanma o'rtasidagi farq: oddiy tushuntirish",
    "Tannarxni to'g'ri hisoblash va narx belgilash usullari",
    "Cash flow (pul oqimi) nima va uni qanday nazorat qilish kerak",
    "Biznes xarajatlarini qisqartirishning amaliy usullari",
    "Kredit olishdan oldin bilishingiz kerak bo'lgan narsalar",
    "Soliqlar asoslari: kichik biznes uchun tushunarli qo'llanma",

    # Marketing va sotuv
    "Mijozlarni qanday jalb qilish: birinchi 100 mijoz strategiyasi",
    "Ijtimoiy tarmoqlarda biznesni qanday reklama qilish",
    "Sotuv voronkasi (funnel) nima va u qanday ishlaydi",
    "Mijozni qaytarish: sadoqatli xaridor bazasini qurish",
    "Brending asoslari: kuchli brend qanday yaratiladi",
    "Kontent-marketing bilan bepul mijoz jalb qilish",
    "Raqobatchilarni qanday tahlil qilish kerak",

    # Boshqaruv va o'sish
    "Birinchi xodimni qanday yollash va boshqarish kerak",
    "Vaqtni boshqarish: tadbirkor uchun samaradorlik usullari",
    "Biznes jarayonlarini avtomatlashtirish: nimadan boshlash",
    "Biznesni kengaytirish (masshtablash) qachon va qanday amalga oshiriladi",
    "Delegatsiya: ishlarni to'g'ri topshirish san'ati",
    "KPI va biznes ko'rsatkichlarini o'lchash asoslari",

    # Onlayn va zamonaviy
    "Onlayn do'kon ochish: bosqichma-bosqich qo'llanma",
    "Marketplace'larda (Uzum, Wildberries) qanday sotish kerak",
    "Telegram orqali biznes yuritish va sotuvni oshirish",
    "Instagram do'koni: 0 dan mijozgacha yo'l",
    "Dropshipping modeli: qanday ishlaydi va kimlar uchun mos",

    # Amaliy ko'nikmalar
    "Muzokara olib borish: kelishuvga erishish texnikalari",
    "Investor bilan qanday gaplashish va taqdimot tayyorlash",
    "Biznesdagi eng ko'p uchraydigan xatolar va ulardan qochish",
    "Tavakkalchilikni (risk) boshqarish asoslari",
    "Mijoz shikoyatlari bilan qanday ishlash kerak",
    "Sheriklik biznesi: afzalliklari, kamchiliklari va qoidalari",
]

SYSTEM_PROMPT = """**Rol:** Sen tajribali o'zbek biznes-murabbiysi va tadbirkorlik bo'yicha o'qituvchisan.

**Vazifa:** Berilgan mavzu bo'yicha o'zbek tadbirkorlari uchun ORIGINAL, amaliy va o'rgatuvchi maqola yoz. Bu yangilik emas — bu ta'lim kontenti: o'quvchi maqolani o'qib, biror amaliy ko'nikma yoki bilim olishi kerak.

**Qoidalar:**
1. **Amaliylik:** Nazariy gap-so'zdan qoch. Aniq qadamlar, misollar, raqamlar va amaliy maslahatlar ber. Iloji bo'lsa O'zbekiston sharoitiga moslashtir.
2. **Tuzilma:** "maqola" maydonida 5-8 paragrafda, aniq sarlavhalar va ro'yxatlar bilan yorit. Markdown ishlatishing mumkin (## sarlavhalar, - ro'yxatlar). Paragraflarni bo'sh qator bilan ajrat.
3. **Xulosa:** "xulosa" maydonida maqolaning asosiy g'oyasini 3-4 jumlada ber.
4. **Amaliy qadam:** "amaliy_ahamiyat" maydonida o'quvchi HOZIROQ qila oladigan 1-2 aniq harakatni yoz.
5. **SEO:** "seo_sarlavha" maydonida qidiruv uchun optimallashtirilgan sarlavha yoz (60-70 belgi).
6. **Sarlavha:** "sarlavha" maydonida jalb qiluvchi, aniq o'zbekcha sarlavha ber.
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


def _generate_with_gemini(topic: str) -> dict:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY sozlanmagan")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": f"Mavzu: {topic}"}]}],
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


def _generate_with_claude(topic: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY or None)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        system=[{"type": "text", "text": SYSTEM_PROMPT}],
        output_config={"format": {"type": "json_schema", "schema": LESSON_SCHEMA}},
        messages=[{"role": "user", "content": f"Mavzu: {topic}"}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def generate_lesson(topic: str) -> dict:
    """Bitta biznes darsi maqolasini yaratadi (yangiliklar bilan bir xil JSON format)."""
    if AI_PROVIDER == "claude":
        result = _generate_with_claude(topic)
    else:
        result = _generate_with_gemini(topic)
    result["ahamiyati"] = 3
    result["kategoriya"] = "biznes-darslari"
    result["teglar"] = [str(t) for t in (result.get("teglar") or [])][:6]
    return result
