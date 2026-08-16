"""/health uchun testlar.

Render va keep-alive bu endpointni muntazam chaqiradi, shuning uchun u
bazaga faqat bitta arzon so'rov yuborishi kerak. Batafsil kontent
statistikasi /health/details da qoladi.
"""
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app import main
from app.database import Base
from app.models import Article


class HealthEndpointTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        db = self.Session()
        db.add(Article(
            title="Dars", slug="dars",
            original_url="internal://dars/dars",
            status="published", tags=["moliya"],
        ))
        db.commit()
        db.close()

        self.statements = []
        event.listen(self.engine, "before_cursor_execute", self._record)

    def _record(self, conn, cursor, statement, params, context, executemany):
        self.statements.append(statement)

    def tearDown(self):
        event.remove(self.engine, "before_cursor_execute", self._record)
        self.engine.dispose()

    def test_reports_ok_when_database_reachable(self):
        with patch.object(main, "SessionLocal", self.Session):
            result = main.health()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["database"], "ok")
        self.assertIn("pipeline", result)

    def test_runs_only_one_cheap_query(self):
        """Asosiy maqsad: COUNT'lar va IN so'rovi endi bajarilmasligi."""
        self.statements.clear()
        with patch.object(main, "SessionLocal", self.Session):
            main.health()

        self.assertEqual(len(self.statements), 1)
        sql = self.statements[0].lower()
        self.assertIn("select 1", sql)
        self.assertNotIn("count", sql)
        self.assertNotIn("articles", sql)

    def test_reports_degraded_without_crashing_when_database_down(self):
        broken = create_engine("postgresql+psycopg2://nobody@127.0.0.1:1/none")
        BrokenSession = sessionmaker(bind=broken)

        with patch.object(main, "SessionLocal", BrokenSession):
            result = main.health()

        self.assertEqual(result["status"], "degraded")
        self.assertEqual(result["database"], "error")
        broken.dispose()

    def test_details_still_returns_content_stats(self):
        with patch.object(main, "SessionLocal", self.Session):
            result = main.health_details()

        self.assertEqual(result["database"], "ok")
        self.assertIsNotNone(result["latest_article_at"])
        self.assertIn("curated_total", result["idea_pipeline"])
        self.assertIn("approved_queue", result["idea_pipeline"])


if __name__ == "__main__":
    unittest.main()
