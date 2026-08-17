"""/health uchun testlar.

Render va keep-alive bu endpointni muntazam chaqiradi, shuning uchun u
bazaga faqat bitta arzon so'rov yuborishi kerak. Batafsil kontent
statistikasi /health/details da qoladi.
"""
import unittest
from datetime import timedelta
from unittest.mock import patch

from fastapi import Response
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app import main
from app.database import Base
from app.models import Article, PipelineRun
from app.utils import utcnow_naive


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
        db = self.Session()
        db.add(PipelineRun(
            trigger="unit-test",
            status="ok",
            created_count=3,
            completed_at=utcnow_naive(),
        ))
        db.commit()
        db.close()

        with patch.object(main, "SessionLocal", self.Session):
            result = main.health_details()

        self.assertEqual(result["database"], "ok")
        self.assertIsNotNone(result["latest_article_at"])
        self.assertIn("curated_total", result["idea_pipeline"])
        self.assertIn("approved_queue", result["idea_pipeline"])
        self.assertEqual(result["pipeline_persistent"]["created_count"], 3)

    def test_pipeline_monitor_reports_ok_for_recent_success(self):
        db = self.Session()
        db.add(PipelineRun(
            trigger="unit-test",
            status="ok",
            created_count=2,
            completed_at=utcnow_naive(),
        ))
        db.commit()
        db.close()

        response = Response()
        with patch.object(main, "SessionLocal", self.Session):
            result = main.pipeline_health(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["pipeline"]["created_count"], 2)

    def test_pipeline_monitor_reports_stale_with_503(self):
        db = self.Session()
        db.add(PipelineRun(
            trigger="unit-test",
            status="ok",
            completed_at=utcnow_naive() - timedelta(hours=3),
        ))
        db.commit()
        db.close()

        response = Response()
        with (
            patch.object(main, "SessionLocal", self.Session),
            patch.object(main, "PIPELINE_STALE_MINUTES", 120),
        ):
            result = main.pipeline_health(response)

        self.assertEqual(response.status_code, 503)
        self.assertEqual(result["status"], "stale")

    def test_pipeline_monitor_reports_missing_history_with_503(self):
        response = Response()
        with patch.object(main, "SessionLocal", self.Session):
            result = main.pipeline_health(response)

        self.assertEqual(response.status_code, 503)
        self.assertEqual(result["status"], "not_started")


if __name__ == "__main__":
    unittest.main()
