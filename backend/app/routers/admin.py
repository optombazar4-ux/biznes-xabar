import secrets
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import ADMIN_TOKEN, admin_is_configured
from ..database import get_db
from ..deps import require_admin
from ..models import Article, Category, Subscription
from ..schemas import ArticleOut, ArticleUpdate, StatsOut
from ..security import create_access_token
from ..services.telegram import send_to_channel
from ..services.email import send_email_digest
from ..cache import invalidate_cache


router = APIRouter(prefix="/api/admin", tags=["admin"])
protected = APIRouter(dependencies=[Depends(require_admin)])


@router.post("/login")
def admin_login(payload: dict = Body(...)):
    """Admin token/parol bilan kirib JWT access_token olish."""
    token = payload.get("token") or payload.get("password", "")
    if not admin_is_configured():
        raise HTTPException(
            status_code=503,
            detail="Admin panel xavfsiz token sozlanguncha o'chirilgan",
        )
    if not secrets.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Noto'g'ri admin token yoki parol")

    access_token = create_access_token(data={"sub": "admin", "role": "admin"})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
    }


def get_article(db: Session, article_id: int) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Maqola topilmadi")
    return article


@protected.get("/articles", response_model=list[ArticleOut])
def list_articles(db: Session = Depends(get_db), status: str | None = None, limit: int = 50, offset: int = 0):
    query = db.query(Article)
    if status:
        query = query.filter(Article.status == status)
    return query.order_by(Article.created_at.desc()).offset(offset).limit(limit).all()


@protected.put("/articles/{article_id}", response_model=ArticleOut)
def update_article(article_id: int, data: ArticleUpdate, db: Session = Depends(get_db)):
    article = get_article(db, article_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(article, field, value)
    db.commit()
    db.refresh(article)
    invalidate_cache()
    return article


@protected.post("/articles/{article_id}/approve", response_model=ArticleOut)
def approve_article(article_id: int, db: Session = Depends(get_db)):
    """Maqolani tasdiqlash — saytga chiqariladi."""
    article = get_article(db, article_id)
    article.status = "published"
    article.published_at = datetime.utcnow()
    db.commit()
    db.refresh(article)
    invalidate_cache()
    return article


@protected.post("/articles/{article_id}/reject", response_model=ArticleOut)
def reject_article(article_id: int, db: Session = Depends(get_db)):
    article = get_article(db, article_id)
    article.status = "rejected"
    db.commit()
    db.refresh(article)
    invalidate_cache()
    return article


@protected.post("/articles/{article_id}/telegram")
def send_article_to_telegram(article_id: int, background: BackgroundTasks, db: Session = Depends(get_db)):
    """Maqolani Telegram kanaliga yuborish."""
    article = get_article(db, article_id)
    try:
        send_to_channel(article)
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))
    article.sent_to_telegram = True
    db.commit()
    return {"ok": True, "xabar": "Telegram kanaliga yuborildi"}


@protected.delete("/articles/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = get_article(db, article_id)
    db.delete(article)
    db.commit()
    invalidate_cache()
    return {"ok": True}



@protected.post("/send-digest")
def send_digest(db: Session = Depends(get_db)):
    """Faol obunachilarga eng so'nggi chop etilgan 5 ta darsdan iborat email dayjest yuboradi."""
    subs = db.query(Subscription).filter(Subscription.is_active.is_(True)).all()
    emails = [s.email for s in subs]
    if not emails:
        return {"ok": True, "sent_count": 0, "xabar": "Faol obunachilar topilmadi"}

    articles = (
        db.query(Article)
        .filter(Article.status == "published")
        .order_by(Article.published_at.desc())
        .limit(5)
        .all()
    )
    art_dicts = [
        {"title": a.title, "summary": a.summary, "slug": a.slug} for a in articles
    ]

    sent_count = send_email_digest(
        to_emails=emails,
        subject="🎓 Biznes Darslari — Eng so'nggi amaliy darslar dayjesti",

        articles=art_dicts,
    )
    return {"ok": True, "sent_count": sent_count, "xabar": f"Dayjest {sent_count} ta obunachiga yuborildi"}


@protected.get("/stats", response_model=StatsOut)

def stats(db: Session = Depends(get_db)):
    by_category = {}
    for category in db.query(Category).all():
        count = db.query(Article).filter(
            Article.category_id == category.id, Article.status == "published"
        ).count()
        if count:
            by_category[category.name] = count

    return StatsOut(
        jami=db.query(Article).count(),
        kutilmoqda=db.query(Article).filter(Article.status == "pending").count(),
        chop_etilgan=db.query(Article).filter(Article.status == "published").count(),
        rad_etilgan=db.query(Article).filter(Article.status == "rejected").count(),
        telegramga_yuborilgan=db.query(Article).filter(Article.sent_to_telegram.is_(True)).count(),
        kategoriyalar_boyicha=by_category,
    )


router.include_router(protected)

