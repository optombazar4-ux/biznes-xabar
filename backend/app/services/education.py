"""Biznes darslari generatori — loyihaning markaziy kontent dvigateli.

O'zbek tadbirkorlari uchun biznes ochish va yuritish bo'yicha amaliy, eskirmaydigan
(evergreen) darslar yaratadi. Har bir dars jahon (chet el) eng yaxshi amaliyotiga
asoslanadi, LEKIN O'zbekistonga moslashtiriladi: YaTT/MChJ ro'yxati (soliq.uz),
mahalliy soliqlar, Uzum Market/Payme/Click, so'm, mahalliy misollar.

Mavzular kurator qilingan kurikulumdan olinadi — mavzu takrorlanmaydi.
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

# Kurikulum: (bo'lim_slug, mavzu). Bo'lim sluglari seed.py bilan mos bo'lishi shart.
LESSON_TOPICS = [
    # --- Biznesni boshlash ---
    ("biznesni-boshlash", "Biznesni noldan qanday boshlash: bosqichma-bosqich qo'llanma"),
    ("biznesni-boshlash", "Biznes g'oyasini sinovdan o'tkazish: bozorni qanday tekshirish kerak"),
    ("biznesni-boshlash", "Soddalashtirilgan biznes-reja qanday yoziladi (shablon bilan)"),
    ("biznesni-boshlash", "YaTT va MChJ farqi: qaysi biri sizga mos"),
    ("biznesni-boshlash", "O'zbekistonda biznesni ro'yxatdan o'tkazish: bosqichma-bosqich"),
    ("biznesni-boshlash", "Kam kapital bilan boshlanadigan biznes turlari"),
    ("biznesni-boshlash", "Boshlang'ich kapitalni qanday hisoblash va topish"),

    # --- Moliya va hisob ---
    ("moliya", "Tannarxni to'g'ri hisoblash va narx belgilash usullari"),
    ("moliya", "Foyda va aylanma o'rtasidagi farq: oddiy tushuntirish"),
    ("moliya", "Cash flow (pul oqimi)ni qanday nazorat qilish kerak"),
    ("moliya", "O'zbekistonda kichik biznes soliqlari: asosiy tushunchalar"),
    ("moliya", "Biznes xarajatlarini qisqartirishning amaliy usullari"),
    ("moliya", "Kredit yoki mikroqarz olishdan oldin bilish kerak bo'lgan narsalar"),
    ("moliya", "Biznes hisobini shaxsiy puldan qanday ajratish kerak"),

    # --- Marketing va sotuv ---
    ("marketing-sotuv", "Birinchi 100 mijozni qanday jalb qilish"),
    ("marketing-sotuv", "Instagram orqali biznesni reklama qilish va sotish"),
    ("marketing-sotuv", "Telegram kanal va bot orqali sotuvni oshirish"),
    ("marketing-sotuv", "Sotuv voronkasi (funnel) nima va u qanday ishlaydi"),
    ("marketing-sotuv", "Kuchli brend qanday yaratiladi: brending asoslari"),
    ("marketing-sotuv", "Sodiq mijozlar bazasini qurish va mijozni qaytarish"),
    ("marketing-sotuv", "Raqobatchilarni qanday to'g'ri tahlil qilish kerak"),
    ("marketing-sotuv", "Arzon va bepul marketing usullari"),

    # --- Boshqaruv va o'sish ---
    ("boshqaruv", "Birinchi xodimni qanday yollash va boshqarish kerak"),
    ("boshqaruv", "Delegatsiya: ishlarni to'g'ri topshirish san'ati"),
    ("boshqaruv", "Biznes jarayonlarini avtomatlashtirish: nimadan boshlash"),
    ("boshqaruv", "Biznesni masshtablash qachon va qanday amalga oshiriladi"),
    ("boshqaruv", "KPI va asosiy biznes ko'rsatkichlarini o'lchash"),
    ("boshqaruv", "Tadbirkor uchun vaqtni boshqarish va samaradorlik"),

    # --- Onlayn biznes ---
    ("onlayn-biznes", "Onlayn do'kon ochish: bosqichma-bosqich qo'llanma"),
    ("onlayn-biznes", "Uzum Market'da qanday sotish kerak"),
    ("onlayn-biznes", "Wildberries orqali O'zbekistondan sotish"),
    ("onlayn-biznes", "Payme va Click orqali onlayn to'lovlarni ulash"),
    ("onlayn-biznes", "Dropshipping modeli: qanday ishlaydi va kimga mos"),
    ("onlayn-biznes", "Ijtimoiy tarmoq do'koni: 0 dan birinchi mijozgacha"),

    # --- Amaliy ko'nikmalar ---
    ("amaliy-konikmalar", "Muzokara olib borish va kelishuvga erishish texnikalari"),
    ("amaliy-konikmalar", "Investor bilan gaplashish va taqdimot (pitch) tayyorlash"),
    ("amaliy-konikmalar", "Tadbirkorlar ko'p yo'l qo'yadigan xatolar va ulardan qochish"),
    ("amaliy-konikmalar", "Risk (tavakkalchilik)ni boshqarish asoslari"),
    ("amaliy-konikmalar", "Mijoz shikoyatlari bilan qanday ishlash kerak"),
    ("amaliy-konikmalar", "Sheriklik biznesi: qoidalari, afzalliklari va kamchiliklari"),
]

SYSTEM_PROMPT = """**Rol:** Sen tajribali o'zbek biznes-murabbiysan. O'zbekistonda biznes ochish va yuritish amaliyotini, mahalliy qonunchilik va bozor sharoitini yaxshi bilasan.

**Vazifa:** Berilgan mavzu bo'yicha o'zbek tadbirkorlari uchun ORIGINAL, amaliy va o'rgatuvchi dars yoz. Bu yangilik emas — bu eskirmaydigan ta'lim kontenti. O'quvchi darsni o'qib, aniq bir ko'nikma yoki bilim olishi kerak.

**Asosiy tamoyil — jahon tajribasi + O'zbekiston sharoiti:**
- Darsni jahon miqyosida isbotlangan eng yaxshi amaliyot va tamoyillarga (best practices) asosla.
- LEKIN uni DOIM O'zbekiston sharoitiga moslashtir: mahalliy ro'yxatdan o'tish (YaTT/MChJ, soliq.uz), O'zbekiston soliqlari, mahalliy to'lov tizimlari (Payme, Click, Uzum), marketpleyslar (Uzum Market, Wildberries), so'mdagi realistik raqamlar va O'zbekistonga xos misollar.
- Umumiy nazariy gapdan qoch — mahalliy tadbirkor ertaga qo'llay oladigan aniq qadamlarni ber.

**Qoidalar:**
1. **Amaliylik:** Aniq qadamlar, misollar, raqamlar va tekshiruv ro'yxatlari (checklist) ber.
2. **Tuzilma:** "maqola" maydonida 6-9 paragrafda, aniq sarlavhalar (## ) va ro'yxatlar (- ) bilan yorit. Markdown ishlat. Paragraflarni bo'sh qator bilan ajrat.
3. **Xulosa:** "xulosa" maydonida darsning asosiy g'oyasini 3-4 jumlada ber.
4. **Amaliy qadam:** "amaliy_ahamiyat" maydonida o'quvchi HOZIROQ qila oladigan 1-2 aniq harakatni yoz.
5. **SEO:** "seo_sarlavha" maydonida qidiruv uchun optimallashtirilgan sarlavha yoz (60-70 belgi).
6. **Sarlavha:** "sarlavha" maydonida jalb qiluvchi, aniq o'zbekcha sarlavha ber.
7. **Teglar:** "teglar" maydonida 3-6 ta mavzuga oid teg.
8. **Til:** DOIM lotin alifbosidagi o'zbek tilida yoz.
9. **Format:** Javobni qat'iy JSON formatida qaytar."""

LESSON_SCHEMA = {
    "type": "object",
    "properties": {
        "sarlavha": {"type": "string"},
        "seo_sarlavha": {"type": "string"},
        "xulosa": {"type": "string"},
        "maqola": {"type": "string"},
        "amaliy_ahamiyat": {"type": "string"},
        "teglar": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "sarlavha", "seo_sarlavha", "xulosa",
        "maqola", "amaliy_ahamiyat", "teglar",
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
    import anthropic  # ixtiyoriy provayder — faqat kerak bo'lganda import qilinadi

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY or None)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        output_config={"format": {"type": "json_schema", "schema": LESSON_SCHEMA}},
        messages=[{"role": "user", "content": f"Mavzu: {topic}"}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Model darsdan bosh tortdi (refusal)")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def generate_lesson(topic: str) -> dict:
    """Bitta biznes darsi maqolasini yaratadi."""
    if AI_PROVIDER == "claude":
        result = _generate_with_claude(topic)
    else:
        result = _generate_with_gemini(topic)
    result["teglar"] = [str(t) for t in (result.get("teglar") or [])][:6]
    return result
