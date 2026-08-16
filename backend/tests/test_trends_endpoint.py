"""/api/news/trends uchun testlar.

Bosh sahifa bu endpointni har bir tashrifda chaqiradi, shuning uchun u
maqola matnini emas, faqat `tags` ustunini o'qishi kerak.
"""
import unittest

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Article
from app.routers.news import trend_topics


class TrendTopicsTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

        self.db.add_all([
            Article(
                title="Dars 1", slug="dars-1",
                original_url="internal://dars/dars-1",
                status="published", tags=["moliya", "soliq"],
                content="A" * 5000,
            ),
            Article(
                title="Dars 2", slug="dars-2",
                original_url="internal://dars/dars-2",
                status="published", tags=["moliya", "marketing"],
                content="B" * 5000,
            ),
            Article(
                title="Dars 3", slug="dars-3",
                original_url="internal://dars/dars-3",
                status="published", tags=["moliya"],
                content="C" * 5000,
            ),
            # Chop etilmagan maqola hisoblanmasligi kerak
            Article(
                title="Kutilmoqda", slug="pending-1",
                original_url="internal://dars/pending-1",
                status="pending", tags=["yashirin"],
                content="D" * 5000,
            ),
            # Tegsiz maqola xato bermasligi kerak
            Article(
                title="Tegsiz", slug="tegsiz",
                original_url="internal://dars/tegsiz",
                status="published", tags=None,
                content="E" * 5000,
            ),
        ])
        self.db.commit()

        self.statements = []
        event.listen(self.engine, "before_cursor_execute", self._record)

    def _record(self, conn, cursor, statement, params, context, executemany):
        self.statements.append(statement)

    def tearDown(self):
        event.remove(self.engine, "before_cursor_execute", self._record)
        self.db.close()
        self.engine.dispose()

    def test_counts_tags_from_published_articles_only(self):
        trends = trend_topics(self.db)

        counts = {item["teg"]: item["soni"] for item in trends}
        self.assertEqual(counts["moliya"], 3)
        self.assertEqual(counts["soliq"], 1)
        self.assertEqual(counts["marketing"], 1)
        self.assertNotIn("yashirin", counts)

    def test_results_are_sorted_by_frequency(self):
        trends = trend_topics(self.db)

        self.assertEqual(trends[0]["teg"], "moliya")
        self.assertEqual(trends[0]["soni"], 3)

    def test_limit_is_respected(self):
        self.assertEqual(len(trend_topics(self.db, limit=2)), 2)

    def test_query_does_not_select_article_content(self):
        """Asosiy maqsad: matn ustuni umuman o'qilmasligi."""
        self.statements.clear()
        trend_topics(self.db)

        self.assertEqual(len(self.statements), 1)
        sql = self.statements[0].lower()
        self.assertIn("articles.tags", sql)
        self.assertNotIn("articles.content", sql)
        self.assertNotIn("articles.summary", sql)


if __name__ == "__main__":
    unittest.main()
