"""Ommaviy darslar API — faqat chop etilgan darslar."""

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Article, Category
from ..schemas import ArticleOut
from ..services.education import LESSON_TOPICS

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
    """Sarlavha, xulosa va matn bo'yicha qidiruv."""
    pattern = f"%{q}%"
    return (
        published(db)
        .filter(or_(
            Article.title.ilike(pattern),
            Article.summary.ilike(pattern),
            Article.content.ilike(pattern),
        ))
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
