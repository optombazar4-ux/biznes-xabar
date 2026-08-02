"""Ommaviy darslar API — faqat chop etilgan darslar."""

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Article, Category
from ..schemas import ArticleOut, SubscribeIn
from ..cache import cache_response
from ..services.education import LESSON_TOPICS
from ..services.audio import generate_article_audio



router = APIRouter(prefix="/api/news", tags=["darslar"])

# Mavzu -> kurikulumdagi tartib raqami (kurs ketma-ketligi uchun)
_TOPIC_ORDER = {topic: i for i, (_, topic) in enumerate(LESSON_TOPICS)}


def published(db: Session):
    return db.query(Article).filter(Article.status == "published")


@router.get("", response_model=list[ArticleOut])
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

    if tartib == "kurs":
        # Kurikulum tartibida: mavzu ro'yxatidagi o'rniga qarab saralaymiz
        lessons = query.all()
        lessons.sort(key=lambda a: _TOPIC_ORDER.get(a.original_title, 10_000))
        return lessons[offset:offset + limit]

    return (
        query.order_by(Article.published_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/trends")
def trend_topics(db: Session = Depends(get_db), limit: int = 15):
    """Ommabop teglar — barcha darslar bo'yicha eng ko'p uchraganlari."""
    articles = published(db).all()
    counter = Counter(tag for a in articles for tag in (a.tags or []))
    return [{"teg": tag, "soni": count} for tag, count in counter.most_common(limit)]


@router.get("/search", response_model=list[ArticleOut])
def search_lessons(q: str, db: Session = Depends(get_db), limit: int = Query(default=20, le=100)):
    """Sarlavha, xulosa, matn va amaliy ahamiyat bo'yicha takomillashtirilgan qidiruv."""
    clean_q = q.strip()
    if not clean_q:
        return []

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
            published(db)
            .filter(ts_vector.op("@@")(ts_query))
            .order_by(func.ts_rank_cd(ts_vector, ts_query).desc(), Article.published_at.desc())
            .limit(limit)
            .all()
        )
        if results:
            return results

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

    return (
        published(db)
        .filter(and_(*filters))
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )


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


@router.get("/{slug}", response_model=ArticleOut)
def lesson_detail(slug: str, db: Session = Depends(get_db)):
    article = published(db).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return article


@router.get("/{slug}/related", response_model=list[ArticleOut])
def related_lessons(slug: str, db: Session = Depends(get_db), limit: int = 4):
    """Mavzuga oid va o'xshash darslarni qaytaradi."""
    article = published(db).filter(Article.slug == slug).first()
    if not article:
        return []

    # 1. Shu kategoriyadagi boshqa maqolalar
    related = (
        published(db)
        .filter(Article.id != article.id)
        .filter(Article.category_id == article.category_id)
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )

    # 2. Agar kategoriya bo'yicha kam bo'lsa, eng so'nggi boshqa maqolalar bilan to'ldiramiz
    if len(related) < limit:
        existing_ids = {a.id for a in related} | {article.id}
        fillers = (
            published(db)
            .filter(Article.id.not_in(existing_ids))
            .order_by(Article.published_at.desc())
            .limit(limit - len(related))
            .all()
        )
        related.extend(fillers)

    return related


@router.get("/{slug}/audio")
def lesson_audio(slug: str, db: Session = Depends(get_db)):
    """Dars matnidan O'zbekcha MP3 audio yaratadi va kesh URL qaytaradi."""
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
def subscribe_newsletter(data: SubscribeIn, db: Session = Depends(get_db)):
    """Email obunasini ro'yxatdan o'tkazish."""
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

