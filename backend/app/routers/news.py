"""Ommaviy darslar API — faqat chop etilgan darslar."""

from collections import Counter
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Article, Category
from ..schemas import ArticleListOut, ArticleOut, SitemapArticleOut, SubscribeIn
from ..services.education import LESSON_TOPICS
from ..services.audio import generate_article_audio
from ..rate_limit import enforce_rate_limit



router = APIRouter(prefix="/api/news", tags=["darslar"])

# Mavzu -> kurikulumdagi tartib raqami (kurs ketma-ketligi uchun)
_TOPIC_ORDER = {topic: i for i, (_, topic) in enumerate(LESSON_TOPICS)}

# Kurs tartibini bazaning o'zida saralash uchun CASE ifodasi. Ilgari bu
# saralash Python'da bajarilardi va buning uchun kategoriyadagi BARCHA
# maqola to'liq matni bilan yuklanardi; endi faqat kerakli sahifa o'qiladi.
_COURSE_ORDER = case(_TOPIC_ORDER, value=Article.original_title, else_=10_000)


def published(db: Session):
    return db.query(Article).filter(Article.status == "published")


# Ro'yxatlarda maqola matni kerak emas — undan faqat o'qish vaqti hisoblanardi.
# Matnni bazadan tortish o'rniga uzunligini olamiz: o'zbekcha darslarda
# o'rtacha ~8.1 belgi/so'z va ~160 so'z/daqiqa, ya'ni ~1300 belgi/daqiqa.
# Mavjud 116 ta maqolada tekshirilganda farq 1 daqiqadan oshmadi.
CHARS_PER_MINUTE = 1300

_LIST_COLUMNS = (
    Article.id,
    Article.title,
    Article.slug,
    Article.summary,
    Article.tags,
    Article.image_url,
    Article.importance,
    Article.status,
    Article.published_at,
    Article.created_at,
    func.length(func.coalesce(Article.content, "")).label("content_length"),
    Category.id.label("category_id"),
    Category.name.label("category_name"),
    Category.slug.label("category_slug"),
)


def _list_item(row) -> dict:
    """Yengil qatorni ArticleListOut ko'rinishiga o'giradi."""
    return {
        "id": row.id,
        "title": row.title,
        "slug": row.slug,
        "summary": row.summary or "",
        "tags": row.tags or [],
        "image_url": row.image_url,
        "importance": row.importance,
        "status": row.status,
        "reading_minutes": max(
            1, int((row.content_length or 0) / CHARS_PER_MINUTE + 0.5)
        ),
        "category": (
            {
                "id": row.category_id,
                "name": row.category_name,
                "slug": row.category_slug,
            }
            if row.category_id
            else None
        ),
        "published_at": row.published_at,
        "created_at": row.created_at,
    }


@router.get("", response_model=list[ArticleListOut])
def latest_lessons(
    db: Session = Depends(get_db),
    kategoriya: str | None = None,
    tartib: str | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
):
    """Darslar ro'yxati (ixtiyoriy bo'lim filtri bilan).

    tartib="kurs" bo'lsa — kurikulum ketma-ketligida (kurs uchun); aks holda
    eng so'nggi birinchi.
    """
    query = published(db)
    if kategoriya:
        query = query.join(Category).filter(Category.slug == kategoriya)
    else:
        query = query.outerjoin(Category)
    query = query.with_entities(*_LIST_COLUMNS)

    if tartib == "kurs":
        # Kurikulum tartibida: saralash bazada bajariladi, Article.id esa
        # bir xil tartib raqamli darslar uchun barqaror ketma-ketlik beradi.
        query = query.order_by(_COURSE_ORDER, Article.id)
    else:
        query = query.order_by(Article.published_at.desc())

    return [_list_item(row) for row in query.offset(offset).limit(limit).all()]


@router.get("/trends")
def trend_topics(db: Session = Depends(get_db), limit: int = 15):
    """Ommabop teglar — barcha darslar bo'yicha eng ko'p uchraganlari.

    Bosh sahifa har bir tashrifda shu endpointni chaqiradi, shuning uchun
    faqat `tags` ustuni o'qiladi — maqola matnini tortish maqolalar soni
    ortishi bilan javobni og'irlashtirardi.
    """
    rows = published(db).with_entities(Article.tags).all()
    counter = Counter(tag for (tags,) in rows for tag in (tags or []))
    return [{"teg": tag, "soni": count} for tag, count in counter.most_common(limit)]


@router.get("/search", response_model=list[ArticleListOut])
def search_lessons(q: str, db: Session = Depends(get_db), limit: int = Query(default=20, le=100)):
    """Sarlavha, xulosa, matn va amaliy ahamiyat bo'yicha takomillashtirilgan qidiruv.

    Qidiruv matn bo'yicha bazada bajariladi, lekin matnning o'zi javobga
    qaytarilmaydi va bazadan o'qilmaydi.
    """
    clean_q = q.strip()
    if not clean_q:
        return []

    def _light(query):
        return query.outerjoin(Category).with_entities(*_LIST_COLUMNS)

    bind = db.get_bind()
    # 1. PostgreSQL Full-Text Search (FTS)
    if bind and bind.dialect.name == "postgresql":
        ts_vector = func.to_tsvector(
            "simple",
            func.coalesce(Article.title, "")
            + " "
            + func.coalesce(Article.summary, "")
            + " "
            + func.coalesce(Article.content, "")
            + " "
            + func.coalesce(Article.practical_note, ""),
        )
        ts_query = func.websearch_to_tsquery("simple", clean_q)
        results = (
            _light(published(db).filter(ts_vector.op("@@")(ts_query)))
            .order_by(func.ts_rank_cd(ts_vector, ts_query).desc(), Article.published_at.desc())
            .limit(limit)
            .all()
        )
        if results:
            return [_list_item(row) for row in results]

    # 2. SQLite / Multi-word Wildcard Fallback
    keywords = [k for k in clean_q.split() if len(k) > 1]
    if not keywords:
        keywords = [clean_q]

    filters = []
    for kw in keywords:
        pat = f"%{kw}%"
        filters.append(
            or_(
                Article.title.ilike(pat),
                Article.summary.ilike(pat),
                Article.content.ilike(pat),
                Article.practical_note.ilike(pat),
            )
        )

    rows = (
        _light(published(db).filter(and_(*filters)))
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )
    return [_list_item(row) for row in rows]


@router.get("/rss")
def get_rss_feed(db: Session = Depends(get_db)):
    """Agregatorlar uchun RSS feed."""
    import html
    from fastapi import Response
    from ..config import FRONTEND_ORIGIN

    articles = (
        published(db)
        .order_by(Article.published_at.desc())
        .limit(50)
        .all()
    )

    rss_items = []
    for article in articles:
        pub_date = article.published_at.strftime("%a, %d %b %Y %H:%M:%S GMT") if article.published_at else ""
        link = f"{FRONTEND_ORIGIN}/maqola/{article.slug}"
        rss_items.append(
            f"<item>\n"
            f"  <title>{html.escape(article.title)}</title>\n"
            f"  <link>{link}</link>\n"
            f"  <guid isPermaLink=\"true\">{link}</guid>\n"
            f"  <description>{html.escape(article.summary)}</description>\n"
            f"  <pubDate>{pub_date}</pubDate>\n"
            f"</item>"
        )

    rss_items_str = "\n".join(rss_items)
    rss_xml = (
        f"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
        f"<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n"
        f"<channel>\n"
        f"  <title>Biznes Darslari — O'zbekistonda biznes ochish va yuritish</title>\n"
        f"  <link>{FRONTEND_ORIGIN}</link>\n"
        f"  <description>O'zbek tadbirkorlari uchun amaliy biznes darslari — jahon tajribasi asosida.</description>\n"
        f"  <language>uz</language>\n"
        f"  {rss_items_str}\n"
        f"</channel>\n"
        f"</rss>"
    )
    return Response(content=rss_xml, media_type="application/xml")


def _matcher_score(article: Article, budget: str, location: str, sector: str) -> int:
    tags = {str(tag).lower() for tag in (article.tags or [])}
    text_value = " ".join(
        [article.title or "", article.summary or "", article.content or ""]
    ).lower()
    score = 0

    amounts = [
        float(value.replace(",", "."))
        for value in re.findall(r"(\d+(?:[.,]\d+)?)\s*mln", text_value)
    ]
    if budget == "low" and ("5 mln gacha" in tags or any(value <= 5 for value in amounts)):
        score += 1
    elif budget == "medium" and any(5 < value <= 20 for value in amounts):
        score += 1
    elif budget == "large" and any(value > 20 for value in amounts):
        score += 1

    if location == "any" or location in tags or location in text_value:
        score += 1
    if sector in tags or sector in text_value:
        score += 1
    return score


@router.get("/stats")
def lesson_stats(db: Session = Depends(get_db)):
    """Ommaviy statistika — bosh sahifa uchun (darslar va g'oyalar soni)."""
    total = published(db).count()
    ideas = (
        published(db)
        .join(Category)
        .filter(Category.slug == "biznes-goyalari")
        .count()
    )
    return {"jami_darslar": total, "biznes_goyalar": ideas}


@router.get("/sitemap", response_model=list[SitemapArticleOut])
def sitemap_lessons(db: Session = Depends(get_db)):
    """Sitemap uchun barcha chop etilgan darslarning yengil ro'yxati."""
    rows = (
        published(db)
        .outerjoin(Category)
        .with_entities(
            Article.slug,
            Category.slug.label("category_slug"),
            Article.tags,
            Article.published_at,
            Article.created_at,
        )
        .order_by(Article.published_at.desc(), Article.id.desc())
        .all()
    )
    return [
        {
            "slug": row.slug,
            "category_slug": row.category_slug or "biznesni-boshlash",
            "tags": row.tags or [],
            "published_at": row.published_at,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/ideas/match", response_model=list[ArticleOut])
def match_business_ideas(
    budget: str = Query(pattern="^(low|medium|large)$"),
    location: str = Query(pattern="^(uydan|onlayn|qishloq|any)$"),
    sector: str = Query(pattern="^(xizmat|savdo|ishlab chiqarish)$"),
    db: Session = Depends(get_db),
):
    """Statik da'volarsiz, tanlangan mezonlar bo'yicha g'oyalarni saralaydi."""
    candidates = (
        published(db)
        .join(Category)
        .filter(Category.slug == "biznes-goyalari")
        .all()
    )
    ranked = sorted(
        ((article, _matcher_score(article, budget, location, sector)) for article in candidates),
        key=lambda item: (item[1], item[0].published_at or item[0].created_at),
        reverse=True,
    )
    return [article for article, score in ranked if score >= 2][:3]


@router.get("/{slug}", response_model=ArticleOut)
def lesson_detail(slug: str, db: Session = Depends(get_db)):
    article = published(db).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return article


@router.get("/{slug}/related", response_model=list[ArticleListOut])
def related_lessons(slug: str, db: Session = Depends(get_db), limit: int = 4):
    """Mavzuga oid va o'xshash darslarni qaytaradi."""
    # Manba maqoladan faqat id va kategoriya kerak — matnini o'qimaymiz.
    current = (
        published(db)
        .filter(Article.slug == slug)
        .with_entities(Article.id, Article.category_id)
        .first()
    )
    if not current:
        return []

    def _light(query):
        return query.outerjoin(Category).with_entities(*_LIST_COLUMNS)

    # 1. Shu kategoriyadagi boshqa maqolalar
    related = (
        _light(
            published(db)
            .filter(Article.id != current.id)
            .filter(Article.category_id == current.category_id)
        )
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )

    # 2. Agar kategoriya bo'yicha kam bo'lsa, eng so'nggi boshqa maqolalar bilan to'ldiramiz
    if len(related) < limit:
        existing_ids = {row.id for row in related} | {current.id}
        fillers = (
            _light(published(db).filter(Article.id.not_in(existing_ids)))
            .order_by(Article.published_at.desc())
            .limit(limit - len(related))
            .all()
        )
        related.extend(fillers)

    return [_list_item(row) for row in related]


@router.get("/{slug}/audio")
def lesson_audio(slug: str, request: Request, db: Session = Depends(get_db)):
    """Dars matnidan O'zbekcha MP3 audio yaratadi va kesh URL qaytaradi."""
    enforce_rate_limit(request, "lesson-audio", limit=10, window_seconds=60 * 60)
    article = published(db).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    audio_url = generate_article_audio(
        slug=article.slug,
        title=article.title,
        summary=article.summary,
        practical_note=article.practical_note,
    )
    if not audio_url:
        raise HTTPException(status_code=500, detail="Audio generatsiyasida xatolik")

    return {"ok": True, "audio_url": audio_url}




@router.post("/subscribe")
def subscribe_newsletter(data: SubscribeIn, request: Request, db: Session = Depends(get_db)):
    """Email obunasini ro'yxatdan o'tkazish."""
    enforce_rate_limit(request, "newsletter-subscribe", limit=5, window_seconds=60 * 60)
    from ..models import Subscription
    existing = db.query(Subscription).filter(Subscription.email == data.email).first()
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.commit()
        return {"ok": True, "xabar": "Siz allaqachon obuna bo'lgansiz!"}

    sub = Subscription(email=data.email, is_active=True)
    db.add(sub)
    db.commit()
    return {"ok": True, "xabar": "Rahmat! Email obunangiz muvaffaqiyatli qabul qilindi."}
