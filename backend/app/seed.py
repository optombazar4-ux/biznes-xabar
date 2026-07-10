from sqlalchemy.orm import Session

from .models import Article, Category

# Biznes darslari kurikulumi bo'limlari (yangilik kategoriyalari emas).
# Sluglar education.py dagi LESSON_TOPICS bilan mos bo'lishi shart.
CATEGORIES = [
    ("Biznesni boshlash", "biznesni-boshlash"),
    ("Moliya va hisob", "moliya"),
    ("Marketing va sotuv", "marketing-sotuv"),
    ("Boshqaruv va o'sish", "boshqaruv"),
    ("Onlayn biznes", "onlayn-biznes"),
    ("Amaliy ko'nikmalar", "amaliy-konikmalar"),
]

# Darslar shu bilan belgilanadi (yangiliklardan ajratish uchun)
LESSON_URL_PREFIX = "internal://dars/"


def seed_categories(db: Session) -> None:
    existing = {slug for (slug,) in db.query(Category.slug).all()}
    for name, slug in CATEGORIES:
        if slug not in existing:
            db.add(Category(name=name, slug=slug))
    db.commit()


def prune_legacy_content(db: Session) -> None:
    """Eski yangilik kontentini tozalaydi (loyiha ta'lim platformasiga o'tgach).

    Idempotent: darslar (internal://dars/...) saqlanadi, qolgan barcha eski
    yangilik maqolalari va kurikulumga kirmagan eski kategoriyalar o'chiriladi.
    Tozalash tugagach keyingi chaqiruvlar hech narsa o'chirmaydi.
    """
    # 1) Dars bo'lmagan (yangilik) maqolalarni o'chirish
    removed = (
        db.query(Article)
        .filter(~Article.original_url.like(f"{LESSON_URL_PREFIX}%"))
        .delete(synchronize_session=False)
    )

    # 2) Kurikulumga kirmagan eski kategoriyalarni o'chirish (endi maqolasiz)
    keep_slugs = {slug for _, slug in CATEGORIES}
    stale = db.query(Category).filter(~Category.slug.in_(keep_slugs)).all()
    for category in stale:
        db.delete(category)

    db.commit()
    if removed or stale:
        print(f"🧹 Tozalandi: {removed} ta eski yangilik, {len(stale)} ta eski kategoriya o'chirildi")
