"""Biznes darslari quvuri: kurikulum mavzularini asta-sekin sifatli darslar
bilan to'ldiradi.

Har ishga tushganda hali yoritilmagan mavzulardan bir nechtasini tanlaydi,
AI orqali dars yaratadi va saqlaydi. Barcha mavzular yoritilgach — hech narsa
qilmaydi.

AUTO_PUBLISH=true (standart) bo'lsa darslar darhol saytga chiqadi va Telegram
kanalga yuboriladi (AUTO_TELEGRAM=true bo'lsa).

Ishga tushirish:  python -m app.pipeline
Muntazam ishlashi uchun cron'ga qo'ying, masalan har soatda:
  0 * * * * cd /path/backend && .venv/bin/python -m app.pipeline
"""

import os
import random
from datetime import datetime

from .config import AUTO_PUBLISH, AUTO_TELEGRAM, TELEGRAM_BOT_TOKEN
from .database import Base, SessionLocal, engine
from .models import Article, Category
from .seed import prune_legacy_content, seed_categories
from .services.education import LESSON_TOPICS, generate_lesson
from .services.telegram import send_to_channel
from .utils import slugify

# Har ishga tushganda ko'pi bilan shuncha yangi dars yaratiladi (xarajat/sur'at nazorati)
LESSON_BATCH_PER_RUN = int(os.getenv("LESSON_BATCH_PER_RUN", "3"))


def _create_lesson(db, categories, section_slug: str, topic: str) -> Article | None:
    """Bitta mavzu bo'yicha dars yaratib saqlaydi. Xatoda None qaytaradi."""
    print(f"🎓 Dars yaratilmoqda: {topic[:60]}")
    try:
        lesson = generate_lesson(topic)
    except Exception as error:
        print(f"   ✗ Dars yaratish xatosi: {error}")
        return None

    slug = slugify(lesson["sarlavha"])
    if db.query(Article).filter(Article.slug == slug).first():
        slug = f"{slug}-dars"

    category = categories.get(section_slug)
    article = Article(
        title=lesson["sarlavha"],
        seo_title=lesson["seo_sarlavha"],
        slug=slug,
        summary=lesson["xulosa"],
        content=lesson["maqola"],
        practical_note=lesson["amaliy_ahamiyat"],
        tags=lesson["teglar"],
        importance=3,
        original_title=topic,  # mavzu — takrorlanmaslik uchun kalit
        original_url=f"internal://dars/{slug}",
        source_name="Biznes Darslari",
        image_url=None,
        category_id=category.id if category else None,
        status="published" if AUTO_PUBLISH else "pending",
        published_at=datetime.utcnow() if AUTO_PUBLISH else None,
    )
    db.add(article)
    db.commit()
    print("   ✓ Dars saqlandi" + (" (saytga chiqarildi)" if AUTO_PUBLISH else " (pending)"))
    return article


def run_pipeline(per_feed: int = 0) -> int:
    """Kurikulumdagi yoritilmagan mavzulardan yangi darslar yaratadi.

    (per_feed argumenti eski chaqiruvlar bilan moslik uchun qoldirilgan, ishlatilmaydi.)
    """
    Base.metadata.create_all(engine)
    db = SessionLocal()
    created = 0
    try:
        seed_categories(db)
        prune_legacy_content(db)
        categories = {c.slug: c for c in db.query(Category).all()}

        # Yoritilgan mavzular (original_title = mavzu deb saqlaymiz)
        covered = {t for (t,) in db.query(Article.original_title).all()}
        remaining = [(sec, topic) for (sec, topic) in LESSON_TOPICS if topic not in covered]

        if not remaining:
            print("✅ Kurikulumdagi barcha mavzular yoritilgan — yangi dars yaratilmadi.")
            return 0

        random.shuffle(remaining)
        batch = remaining[:LESSON_BATCH_PER_RUN]
        print(f"📚 {len(remaining)} ta mavzu qoldi. Shu safar {len(batch)} ta dars yaratiladi.")

        for section_slug, topic in batch:
            article = _create_lesson(db, categories, section_slug, topic)
            if not article:
                continue
            created += 1

            if AUTO_PUBLISH and AUTO_TELEGRAM and TELEGRAM_BOT_TOKEN:
                try:
                    send_to_channel(article)
                    article.sent_to_telegram = True
                    db.commit()
                    print("   ✓ Telegram kanalga yuborildi")
                except Exception as error:
                    print(f"   ✗ Telegram xatosi: {error}")

        print(f"\n✅ {created} ta yangi dars yaratildi.")
        return created
    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline()
