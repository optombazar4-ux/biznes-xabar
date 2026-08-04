import os
import sqlite3
import subprocess
import sys
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError
from starlette.requests import Request

import app.config as config
import app.pipeline as pipeline
from app.deps import require_admin
from app.models import Article
from app.rate_limit import enforce_rate_limit
from app.routers.news import _matcher_score
from app.schemas import ArticleUpdate
from app.database import Base
from sqlalchemy import create_engine


class AdminSecurityTests(unittest.TestCase):
    def test_admin_requires_explicit_strong_secret(self):
        with (
            patch.object(config, "ADMIN_TOKEN", ""),
            patch.object(config, "JWT_SECRET_KEY", ""),
        ):
            self.assertFalse(config.admin_is_configured())

        with (
            patch.object(config, "ADMIN_TOKEN", "x" * 32),
            patch.object(config, "JWT_SECRET_KEY", "y" * 32),
        ):
            self.assertTrue(config.admin_is_configured())

    def test_unconfigured_admin_rejects_even_bearer_token(self):
        with patch("app.deps.admin_is_configured", return_value=False):
            with self.assertRaises(HTTPException) as raised:
                require_admin(authorization="Bearer forged", x_admin_token="")
        self.assertEqual(raised.exception.status_code, 503)

    def test_article_importance_is_bounded(self):
        with self.assertRaises(ValidationError):
            ArticleUpdate(importance=6)


class PipelinePolicyTests(unittest.TestCase):
    def test_auto_publish_honors_minimum_importance(self):
        with (
            patch.object(pipeline, "AUTO_PUBLISH", True),
            patch.object(pipeline, "AUTO_PUBLISH_MIN_IMPORTANCE", 4),
        ):
            self.assertFalse(pipeline._should_auto_publish(3))
            self.assertTrue(pipeline._should_auto_publish(4))

    def test_auto_telegram_honors_status_and_importance(self):
        article = Article(
            title="Test",
            slug="test",
            original_url="internal://test",
            status="published",
            importance=4,
        )
        with (
            patch.object(pipeline, "AUTO_TELEGRAM", True),
            patch.object(pipeline, "AUTO_TELEGRAM_MIN_IMPORTANCE", 4),
            patch.object(pipeline, "TELEGRAM_BOT_TOKEN", "token"),
        ):
            self.assertTrue(pipeline._should_auto_telegram(article))
            article.importance = 3
            self.assertFalse(pipeline._should_auto_telegram(article))
            article.importance = 5
            article.status = "pending"
            self.assertFalse(pipeline._should_auto_telegram(article))


class PublicFeatureTests(unittest.TestCase):
    def test_matcher_uses_all_selected_criteria(self):
        article = Article(
            title="Uyda xizmat biznesi",
            summary="Boshlash uchun 10 mln so'm kerak.",
            content="Amaliy reja",
            slug="uyda-xizmat",
            original_url="internal://uyda-xizmat",
            tags=["uydan", "xizmat"],
        )
        self.assertEqual(_matcher_score(article, "medium", "uydan", "xizmat"), 3)
        self.assertEqual(_matcher_score(article, "large", "qishloq", "savdo"), 0)

    def test_rate_limit_returns_429(self):
        request = Request({"type": "http", "client": ("203.0.113.77", 1234)})
        enforce_rate_limit(request, "unit-test", limit=1, window_seconds=60)
        with self.assertRaises(HTTPException) as raised:
            enforce_rate_limit(request, "unit-test", limit=1, window_seconds=60)
        self.assertEqual(raised.exception.status_code, 429)


class MigrationBootstrapTests(unittest.TestCase):
    backend_dir = Path(__file__).resolve().parents[1]

    def run_migration(self, db_path: Path) -> None:
        env = os.environ.copy()
        env["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        subprocess.run(
            [sys.executable, "-m", "app.migrate"],
            cwd=self.backend_dir,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_new_database_migrates_to_head(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "new.db"
            self.run_migration(db_path)
            with closing(sqlite3.connect(db_path)) as connection:
                revision = connection.execute(
                    "SELECT version_num FROM alembic_version"
                ).fetchone()[0]
            self.assertEqual(revision, "0002_add_quiz_and_subscriptions")

    def test_existing_current_schema_is_safely_stamped(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "existing.db"
            temp_engine = create_engine(f"sqlite:///{db_path.as_posix()}")
            Base.metadata.create_all(temp_engine)
            temp_engine.dispose()
            self.run_migration(db_path)
            with closing(sqlite3.connect(db_path)) as connection:
                revision = connection.execute(
                    "SELECT version_num FROM alembic_version"
                ).fetchone()[0]
            self.assertEqual(revision, "0002_add_quiz_and_subscriptions")


if __name__ == "__main__":
    unittest.main()
