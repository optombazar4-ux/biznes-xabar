import unittest
from collections import Counter
from datetime import datetime, timedelta
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.pipeline as pipeline
from app.database import Base
from app.models import Article, IdeaProposal, IdeaProposalRun
from app.services.education import IDEA_FILTERS, IDEA_TOPICS, IDEA_TOPIC_TAGS
from app.services.rss_ideas import (
    _canonical_url,
    _parse_feed,
    _validate_suggestion,
    proposal_batch_is_due,
)
from app.utils import title_tokens


class CuratedCatalogTests(unittest.TestCase):
    def test_catalog_and_filter_coverage(self):
        self.assertGreaterEqual(len(IDEA_TOPIC_TAGS), 50)
        self.assertLessEqual(len(IDEA_TOPIC_TAGS), 100)
        counts = Counter(tag for tags in IDEA_TOPIC_TAGS.values() for tag in tags)
        for idea_filter in IDEA_FILTERS:
            self.assertGreaterEqual(
                counts[idea_filter],
                15,
                f"{idea_filter} filtrida kamida 15 ta g'oya bo'lishi kerak",
            )


class RssParserTests(unittest.TestCase):
    def test_rss_parser_and_tracking_cleanup(self):
        xml = """<?xml version="1.0"?>
        <rss version="2.0"><channel><item>
          <title>Small business subscription trend</title>
          <link>https://example.com/story?utm_source=test&amp;id=7</link>
          <description><![CDATA[<p>Useful <b>business</b> summary.</p>]]></description>
          <pubDate>Mon, 27 Jul 2026 12:00:00 GMT</pubDate>
        </item></channel></rss>"""
        entries = _parse_feed(xml)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["url"], "https://example.com/story?id=7")
        self.assertEqual(entries[0]["summary"], "Useful business summary.")

    def test_invalid_or_non_http_url_is_rejected(self):
        self.assertEqual(_canonical_url("javascript:alert(1)"), "")
        self.assertEqual(_canonical_url(""), "")


class SuggestionValidationTests(unittest.TestCase):
    def setUp(self):
        self.signal = {
            1: {
                "id": 1,
                "title": "Retailers adopt inventory automation",
                "url": "https://example.com/inventory",
                "source": "Example Business",
            }
        }

    def test_valid_low_budget_idea_gets_filter(self):
        raw = {
            "mavzu": "Mahalliy do'konlar uchun zaxira nazorati xizmati",
            "asos": "Kichik do'konlarda mahsulot qoldig'ini nazorat qilish muammosi bor.",
            "filtrlar": ["onlayn", "xizmat"],
            "budjet_min": 1_000_000,
            "budjet_max": 4_500_000,
            "xavflar": "Mijoz odatini o'zgartirish qiyin bo'lishi mumkin.",
            "signal_idlar": [1],
        }
        candidate, notes, is_valid = _validate_suggestion(
            raw,
            seen_titles=[],
            signals_by_id=self.signal,
        )
        self.assertTrue(is_valid, notes)
        self.assertIn("5 mln gacha", candidate["filters"])

    def test_unsafe_idea_is_rejected(self):
        raw = {
            "mavzu": "Telegram orqali crypto signal sotish biznesi",
            "asos": "Tez daromad va'dasi.",
            "filtrlar": ["onlayn", "xizmat"],
            "budjet_min": 1_000_000,
            "budjet_max": 3_000_000,
            "xavflar": "Mijoz pul yo'qotishi mumkin.",
            "signal_idlar": [1],
        }
        _, notes, is_valid = _validate_suggestion(
            raw,
            seen_titles=[],
            signals_by_id=self.signal,
        )
        self.assertFalse(is_valid)
        self.assertTrue(any("taqiqlangan" in note for note in notes))

    def test_near_duplicate_is_rejected(self):
        title = "Mahalliy do'konlar uchun zaxira nazorati xizmati"
        raw = {
            "mavzu": title,
            "asos": "Takroriy g'oya.",
            "filtrlar": ["onlayn", "xizmat"],
            "budjet_min": 1_000_000,
            "budjet_max": 4_000_000,
            "xavflar": "Sinov kerak.",
            "signal_idlar": [1],
        }
        _, notes, is_valid = _validate_suggestion(
            raw,
            seen_titles=[title_tokens(title)],
            signals_by_id=self.signal,
        )
        self.assertFalse(is_valid)
        self.assertTrue(any("o'xshash" in note for note in notes))


class ProposalScheduleTests(unittest.TestCase):
    def test_completed_batch_waits_one_week(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        with sessionmaker(bind=engine)() as db:
            self.assertTrue(proposal_batch_is_due(db))
            run = IdeaProposalRun(status="completed")
            db.add(run)
            db.commit()
            self.assertFalse(proposal_batch_is_due(db))
            run.created_at = datetime.utcnow() - timedelta(days=8)
            db.commit()
            self.assertTrue(proposal_batch_is_due(db))


class PipelineStageTests(unittest.TestCase):
    @staticmethod
    def fake_lesson(topic):
        return {
            "sarlavha": topic,
            "seo_sarlavha": topic,
            "xulosa": "Sinov xulosasi",
            "maqola": "## G'oya qisqacha\nSinov maqolasi",
            "amaliy_ahamiyat": "Bugun bitta mijoz bilan gaplashing.",
            "teglar": ["xizmat"],
        }

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

    def test_curated_catalog_runs_before_rss(self):
        with (
            patch.object(pipeline, "engine", self.engine),
            patch.object(pipeline, "SessionLocal", self.session_factory),
            patch.object(pipeline, "generate_lesson", self.fake_lesson),
            patch.object(pipeline, "create_weekly_proposals") as rss_mock,
            patch.object(pipeline, "_send_to_telegram_if_enabled"),
        ):
            created = pipeline.run_pipeline()
        self.assertEqual(created, pipeline.LESSON_BATCH_PER_RUN)
        rss_mock.assert_not_called()
        with self.session_factory() as db:
            self.assertEqual(db.query(Article).count(), pipeline.LESSON_BATCH_PER_RUN)

    def test_rss_proposal_runs_after_curated_catalog(self):
        with self.session_factory() as db:
            for index, topic in enumerate(IDEA_TOPICS):
                db.add(Article(
                    title=topic,
                    slug=f"covered-{index}",
                    original_title=topic,
                    original_url=f"internal://dars/covered-{index}",
                    source_name="Biznes Darslari",
                    status="published",
                ))
            db.commit()

        def fake_create_proposals(db):
            db.add(IdeaProposal(
                title="Mahalliy ustalar uchun buyurtma boshqaruvi xizmati",
                filters=["onlayn", "xizmat"],
                source_urls=["https://example.com/trend"],
                source_names=["Example Business"],
                source_titles=["Small business service trend"],
                rationale="Buyurtmalarni boshqarish ehtiyoji oshmoqda.",
                estimated_budget_min=1_000_000,
                estimated_budget_max=4_000_000,
                risks="Mijoz topish va ma'lumot xavfsizligi.",
                status="approved",
            ))
            db.commit()
            return 1

        with (
            patch.object(pipeline, "engine", self.engine),
            patch.object(pipeline, "SessionLocal", self.session_factory),
            patch.object(pipeline, "create_weekly_proposals", fake_create_proposals),
            patch.object(
                pipeline,
                "generate_dynamic_idea",
                side_effect=lambda topic, filters, context="": self.fake_lesson(topic),
            ),
            patch.object(pipeline, "_send_to_telegram_if_enabled"),
        ):
            created = pipeline.run_pipeline()
        self.assertEqual(created, 1)
        with self.session_factory() as db:
            proposal = db.query(IdeaProposal).one()
            self.assertEqual(proposal.status, "published")
            self.assertIsNotNone(proposal.article_id)


if __name__ == "__main__":
    unittest.main()
