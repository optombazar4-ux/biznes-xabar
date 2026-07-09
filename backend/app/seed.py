from sqlalchemy.orm import Session

from .models import Category

# Biznes yo'nalishlari bo'yicha kategoriyalar
CATEGORIES = [
    ("Biznes darslari", "biznes-darslari"),
    ("Startaplar", "startaplar"),
    ("Investitsiyalar", "investitsiyalar"),
    ("Moliya va bozorlar", "moliya"),
    ("Marketing", "marketing"),
    ("Boshqaruv", "boshqaruv"),
    ("Elektron tijorat", "elektron-tijorat"),
    ("Iqtisodiyot", "iqtisodiyot"),
    ("Texnologiya biznesi", "texnologiya-biznesi"),
    ("O'zbekiston tadbirkorligi", "uzbekiston-tadbirkorligi"),
]


def seed_categories(db: Session) -> None:
    existing = {slug for (slug,) in db.query(Category.slug).all()}
    for name, slug in CATEGORIES:
        if slug not in existing:
            db.add(Category(name=name, slug=slug))
    db.commit()
