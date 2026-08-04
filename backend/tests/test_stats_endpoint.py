"""Yangi /api/news/stats funksiyasi uchun unit testlar.

Ommaviy statistika faqat chop etilgan (published) darslarni hisoblaydi
va "biznes-goyalari" kategoriyasi alohida ajratiladi.
"""
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Article, Category
from app.routers.news import lesson_stats


class LessonStatsTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        cat_ideas = Category(name="Biznes g'oyalari", slug="biznes-goyalari")
        cat_other = Category(name="Moliya", slug="moliya")
        self.db.add_all([cat_ideas, cat_other])
        self.db.flush()

        self.db.add_all([
            Article(
                title="G'oya 1", slug="goya-1",
                original_url="internal://dars/goya-1",
                status="published", category_id=cat_ideas.id,
            ),
            Article(
                title="G'oya 2", slug="goya-2",
                original_url="internal://dars/goya-2",
                status="published", category_id=cat_ideas.id,
            ),
            Article(
                title="Moliya darsi", slug="moliya-1",
                original_url="internal://dars/moliya-1",
                status="published", category_id=cat_other.id,
            ),
            # Pending maqola hisoblanmasligi kerak
            Article(
                title="Kutilmoqda", slug="pending-1",
                original_url="internal://dars/pending-1",
                status="pending", category_id=cat_ideas.id,
            ),
        ])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_counts_only_published_articles(self):
        stats = lesson_stats(self.db)
        self.assertEqual(stats["jami_darslar"], 3)
        self.assertEqual(stats["biznes_goyalar"], 2)

    def test_empty_database_returns_zeros(self):
        # Barcha maqolalarni o'chirib, bo'sh baza holatini tekshiramiz
        self.db.query(Article).delete()
        self.db.commit()
        stats = lesson_stats(self.db)
        self.assertEqual(stats["jami_darslar"], 0)
        self.assertEqual(stats["biznes_goyalar"], 0)


if __name__ == "__main__":
    unittest.main()
