"""Biznes darslari quvuri: kurikulum mavzularini asta-sekin sifatli darslar
bilan to'ldiradi.

Har ishga tushganda hali yoritilmagan mavzulardan bir nechtasini tanlaydi,
AI orqali dars yaratadi va saqlaydi. Kuratsiya qilingan biznes g'oyalari
tugagach, kunlik RSS trendlaridan validatsiyalangan yangi g'oyalar taklif
qilinadi va maqolaga aylantiriladi.

AUTO_PUBLISH=true bo'lsa minimal muhimlik chegarasidan o'tgan darslar saytga
chiqadi; AUTO_TELEGRAM alohida muhimlik chegarasi bilan kanalga yuboradi.

Ishga tushirish:  python -m app.pipeline
Muntazam ishlashi uchun cron'ga qo'ying, masalan har soatda:
  0 * * * * cd /path/backend && .venv/bin/python -m app.pipeline
"""

import os
import sys
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")


from sqlalchemy import text

from .config import (
    AUTO_PUBLISH,
    AUTO_PUBLISH_MIN_IMPORTANCE,
    AUTO_TELEGRAM,
    AUTO_TELEGRAM_MIN_IMPORTANCE,
    FRONTEND_ORIGIN,
    RSS_IDEA_ENABLED,
    TELEGRAM_BOT_TOKEN,
)
from .database import SessionLocal, engine
from .models import Article, Category, IdeaProposal
from .seed import prune_legacy_content, seed_categories
from .services.education import (
    IDEA_TOPICS,
    LESSON_TOPICS,
    generate_dynamic_idea,
    generate_lesson,
    is_fallback,
)
from .services.rss_ideas import create_weekly_proposals
from .services.telegram import send_to_channel
from .utils import slugify, utcnow_naive

# Har ishga tushganda ko'pi bilan shuncha yangi dars yaratiladi (xarajat/sur'at nazorati)
LESSON_BATCH_PER_RUN = int(os.getenv("LESSON_BATCH_PER_RUN", "3"))
PIPELINE_LOCK_ID = 862_024_071


def _should_auto_publish(importance: int) -> bool:
    return AUTO_PUBLISH and importance >= AUTO_PUBLISH_MIN_IMPORTANCE


def _should_auto_telegram(article: Article) -> bool:
    return (
        article.status == "published"
        and AUTO_TELEGRAM
        and bool(TELEGRAM_BOT_TOKEN)
        and article.importance >= AUTO_TELEGRAM_MIN_IMPORTANCE
    )


def _try_pipeline_lock():
    """Rolling deployda eski va yangi instance bir vaqtda kontent yaratmasin."""
    if engine.dialect.name != "postgresql":
        return None, True
    connection = engine.connect()
    acquired = bool(
        connection.execute(
            text("SELECT pg_try_advisory_lock(:lock_id)"),
            {"lock_id": PIPELINE_LOCK_ID},
        ).scalar()
    )
    return connection, acquired


def _release_pipeline_lock(connection) -> None:
    if connection is None:
        return
    try:
        connection.execute(
            text("SELECT pg_advisory_unlock(:lock_id)"),
            {"lock_id": PIPELINE_LOCK_ID},
        )
    finally:
        connection.close()


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
    importance = 3
    # AI ishlamay zaxira shablon qaytgan bo'lsa, uni saytga chiqarmaymiz —
    # admin ko'rib chiqishi uchun "pending" holatida qoladi.
    from_fallback = is_fallback(lesson)
    if from_fallback:
        print("   ⚠ AI javob bermadi — zaxira shablon pending holatida saqlanadi")
    auto_publish = _should_auto_publish(importance) and not from_fallback
    article = Article(
        title=lesson["sarlavha"],
        seo_title=lesson["seo_sarlavha"],
        slug=slug,
        summary=lesson["xulosa"],
        content=lesson["maqola"],
        practical_note=lesson["amaliy_ahamiyat"],
        tags=lesson["teglar"],
        quiz=lesson.get("quiz", []),
        importance=importance,

        original_title=topic,  # mavzu — takrorlanmaslik uchun kalit
        original_url=f"internal://dars/{slug}",
        source_name="Biznes Darslari",
        image_url=None,
        category_id=category.id if category else None,
        status="published" if auto_publish else "pending",
        published_at=utcnow_naive() if auto_publish else None,
    )
    db.add(article)
    db.commit()
    print("   ✓ Dars saqlandi" + (" (saytga chiqarildi)" if auto_publish else " (pending)"))
    return article


def _proposal_context(proposal: IdeaProposal) -> str:
    signals = "\n".join(
        f"- {name}: {title}"
        for name, title in zip(proposal.source_names or [], proposal.source_titles or [])
    )
    return (
        f"Taklif sababi: {proposal.rationale}\n"
        f"Tekshirilgan budjet: {proposal.estimated_budget_min:,}–"
        f"{proposal.estimated_budget_max:,} so'm\n"
        f"Asosiy xavflar: {proposal.risks}\n"
        f"Trend signallari:\n{signals}"
    )


def _source_notes(proposal: IdeaProposal) -> str:
    lines = []
    for name, url in zip(proposal.source_names or [], proposal.source_urls or []):
        safe_name = str(name).replace("[", "").replace("]", "")[:100]
        if str(url).startswith(("https://", "http://")):
            lines.append(f"- [{safe_name}]({url})")
    if not lines:
        return ""
    return (
        "\n\n## Trend manbalari\n"
        "Ushbu g'oya quyidagi ochiq biznes trendlaridan signal sifatida foydalanib, "
        "O'zbekiston sharoiti uchun mustaqil ishlab chiqildi:\n"
        + "\n".join(lines)
    )


def _create_dynamic_idea(
    db,
    categories,
    proposal: IdeaProposal,
) -> Article | None:
    """Validatsiyadan o'tgan haftalik taklifni maqolaga aylantiradi."""
    print(f"💡 AI g'oya maqolasi yaratilmoqda: {proposal.title[:65]}")
    try:
        lesson = generate_dynamic_idea(
            proposal.title,
            proposal.filters or [],
            context=_proposal_context(proposal),
        )
    except Exception as error:
        print(f"   ✗ AI g'oya maqolasi xatosi: {error}")
        return None

    slug = slugify(lesson["sarlavha"])
    if db.query(Article).filter(Article.slug == slug).first():
        slug = f"{slug}-goya-{proposal.id}"

    category = categories.get("biznes-goyalari")
    importance = 4
    from_fallback = is_fallback(lesson)
    if from_fallback:
        print("   ⚠ AI javob bermadi — zaxira shablon pending holatida saqlanadi")
    auto_publish = _should_auto_publish(importance) and not from_fallback
    article = Article(
        title=lesson["sarlavha"],
        seo_title=lesson["seo_sarlavha"],
        slug=slug,
        summary=lesson["xulosa"],
        content=f"{lesson['maqola']}{_source_notes(proposal)}",
        practical_note=lesson["amaliy_ahamiyat"],
        tags=lesson["teglar"],
        quiz=lesson.get("quiz", []),
        importance=importance,

        original_title=proposal.title,
        original_url=f"internal://dars/ai-goya-{proposal.id}-{slug}",
        source_name=(
            f"RSS trendlar + Biznes Darslari AI: "
            f"{', '.join(proposal.source_names or [])}"
        )[:200],
        image_url=None,
        category_id=category.id if category else None,
        status="published" if auto_publish else "pending",
        published_at=utcnow_naive() if auto_publish else None,
    )
    db.add(article)
    db.flush()
    proposal.article_id = article.id
    proposal.status = "published" if auto_publish else "generated"
    proposal.published_at = utcnow_naive() if auto_publish else None
    db.commit()
    print("   ✓ Validatsiyalangan AI g'oya saqlandi")
    return article


from .services.indexer import ping_search_engines


def _send_to_telegram_if_enabled(db, article: Article) -> None:
    if article.status != "published":
        return

    # IndexNow (Yandex/Bing) va Instant Indexing signali yuborish
    try:
        cat_slug = article.category.slug if article.category else "biznesni-boshlash"
        article_url = f"{FRONTEND_ORIGIN.rstrip('/')}/{cat_slug}/{article.slug}"
        ping_search_engines([article_url])
        print("   ✓ IndexNow (Yandex/Bing) instant indexing signali yuborildi")
    except Exception as err:
        print(f"   ✗ IndexNow xatosi: {err}")

    if not _should_auto_telegram(article):
        return
    try:
        send_to_channel(article)
        article.sent_to_telegram = True
        db.commit()
        print("   ✓ Telegram kanalga yuborildi")
    except Exception as error:
        print(f"   ✗ Telegram xatosi: {error}")



def run_pipeline(per_feed: int = 0) -> int:
    """Kurikulum yoki RSS-AI navbatidan yangi darslar yaratadi.

    (per_feed argumenti eski chaqiruvlar bilan moslik uchun qoldirilgan, ishlatilmaydi.)
    """
    lock_connection, lock_acquired = _try_pipeline_lock()
    if not lock_acquired:
        lock_connection.close()
        print("⏭ Boshqa instance pipeline'ni ishlatyapti — bu safar o'tkazildi.")
        return 0
    db = SessionLocal()
    created = 0
    generation_errors = 0
    try:
        seed_categories(db)
        prune_legacy_content(db)
        categories = {c.slug: c for c in db.query(Category).all()}

        # Yoritilgan mavzular (original_title = mavzu deb saqlaymiz)
        covered = {t for (t,) in db.query(Article.original_title).all()}
        remaining = [
            (section, topic)
            for section, topic in LESSON_TOPICS
            if topic not in covered
        ]
        idea_topics = set(IDEA_TOPICS)
        idea_remaining = [item for item in remaining if item[1] in idea_topics]
        other_remaining = [item for item in remaining if item[1] not in idea_topics]

        # 1-bosqich: 50–100 ta kuratsiya qilingan asosiy g'oyalar katalogi.
        # U tugamaguncha RSS-AI takliflari ishga tushmaydi.
        if idea_remaining:
            random.shuffle(idea_remaining)
            batch = idea_remaining[:LESSON_BATCH_PER_RUN]
            print(
                f"📚 {len(idea_remaining)} ta kuratsiya qilingan g'oya qoldi. "
                f"Shu safar {len(batch)} tasi yaratiladi."
            )
        else:
            batch = []

        # 2-bosqich: katalog tugagach, har kuni RSS trendlaridan 5–10 ta
        # taklif olinadi. Faqat validatsiyadan o'tgan navbat maqolaga aylanadi.
        if not idea_remaining and RSS_IDEA_ENABLED:
            print("📡 Kuratsiya katalogi tayyor. Kunlik RSS trendlar tekshirilmoqda...")
            try:
                create_weekly_proposals(db)
            except Exception as error:
                # RSS yoki taklif AI vaqtincha ishlamasa ham asosiy kurikulum
                # va API ishlashda davom etadi.
                db.rollback()
                print(f"   ✗ Kunlik RSS-AI takliflari xatosi: {error}")
            proposals = (
                db.query(IdeaProposal)
                .filter(IdeaProposal.status == "approved")
                .order_by(IdeaProposal.created_at.asc(), IdeaProposal.id.asc())
                .limit(LESSON_BATCH_PER_RUN)
                .all()
            )
            if proposals:
                for proposal in proposals:
                    article = _create_dynamic_idea(db, categories, proposal)
                    if not article:
                        generation_errors += 1
                        continue
                    created += 1
                    _send_to_telegram_if_enabled(db, article)
                if created == 0 and generation_errors == len(proposals):
                    raise RuntimeError(
                        "Barcha validatsiyalangan AI g'oyalari generatsiyada xatoga uchradi"
                    )
                print(f"\n✅ {created} ta yangi RSS-trend g'oyasi yaratildi.")
                return created

        # Kunlik taklif navbati bo'sh bo'lsa, umumiy biznes kurikulumi davom etadi.
        if not batch and other_remaining:
            random.shuffle(other_remaining)
            batch = other_remaining[:LESSON_BATCH_PER_RUN]
            print(
                f"📚 {len(other_remaining)} ta umumiy dars qoldi. "
                f"Shu safar {len(batch)} tasi yaratiladi."
            )

        if not batch:
            print("✅ Hozircha yangi mavzu yoki tasdiqlangan RSS g'oya yo'q.")
            return 0

        for section_slug, topic in batch:
            article = _create_lesson(db, categories, section_slug, topic)
            if not article:
                generation_errors += 1
                continue
            created += 1

            _send_to_telegram_if_enabled(db, article)

        if batch and created == 0 and generation_errors == len(batch):
            raise RuntimeError("Barcha yangi darslar AI generatsiyasida xatoga uchradi")

        print(f"\n✅ {created} ta yangi dars yaratildi.")
        return created
    finally:
        db.close()
        _release_pipeline_lock(lock_connection)


if __name__ == "__main__":
    run_pipeline()
