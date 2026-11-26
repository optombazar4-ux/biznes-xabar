import unittest
from collections import Counter
from datetime import timedelta
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.pipeline as pipeline
from app.database import Base
from app.models import Article, IdeaProposal, IdeaProposalRun
from app.services import rss_ideas
from app.services.education import (
    IDEA_FILTERS,
    IDEA_TOPICS,
    IDEA_TOPIC_TAGS,
    LESSON_TOPICS,
)
from app.services.rss_ideas import (
    _canonical_url,
    _parse_feed,
    _validate_suggestion,
    proposal_batch_is_due,
)
from app.utils import title_tokens
from app.utils import utcnow_naive


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
    def test_completed_batch_waits_one_day(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        with sessionmaker(bind=engine)() as db:
            with patch("app.services.rss_ideas.RSS_IDEA_INTERVAL_DAYS", 1):
                self.assertTrue(proposal_batch_is_due(db))
                run = IdeaProposalRun(status="completed")
                db.add(run)
                db.commit()
                run.created_at = utcnow_naive() - timedelta(hours=23)
                db.commit()
                self.assertFalse(proposal_batch_is_due(db))
                run.created_at = utcnow_naive() - timedelta(hours=25)
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

    def test_pending_non_fallback_articles_are_published_when_auto_publish_enabled(self):
        with self.session_factory() as db:
            ai_article = Article(
                title="AI tayyorlagan g'oya",
                slug="ai-tayyorlagan-goya",
                original_title="AI tayyorlagan g'oya",
                original_url="internal://dars/ai-tayyorlagan-goya",
                source_name="Biznes Darslari",
                content="## G'oya qisqacha\nHaqiqiy AI matni",
                quiz={
                    "question": "Sinov savoli?",
                    "options": ["Variant A", "Variant B"],
                    "answer_index": 0,
                    "explanation": "Qisqa izoh",
                },
                importance=4,
                status="pending",
            )
            fallback_article = Article(
                title="Zaxira shablon",
                slug="zaxira-shablon",
                original_title="Zaxira shablon",
                original_url="internal://dars/zaxira-shablon",
                source_name="Biznes Darslari",
                content="# Zaxira\n\n## 1. Bozordagi Talab va Konsept\nShablon",
                importance=3,
                status="pending",
            )
            db.add_all([ai_article, fallback_article])
            db.flush()
            proposal = IdeaProposal(
                title="AI tayyorlagan g'oya",
                filters=["onlayn", "xizmat"],
                source_urls=["https://example.com/trend"],
                source_names=["Example Business"],
                source_titles=["Trend"],
                rationale="Sabab",
                estimated_budget_min=1_000_000,
                estimated_budget_max=3_000_000,
                risks="Xavf",
                status="generated",
                article_id=ai_article.id,
            )
            db.add(proposal)
            db.commit()

            with (
                patch.object(pipeline, "AUTO_PUBLISH", True),
                patch.object(pipeline, "AUTO_PUBLISH_MIN_IMPORTANCE", 1),
                patch.object(pipeline, "_send_to_telegram_if_enabled") as tg_mock,
            ):
                published_count = pipeline._publish_pending_articles(db)

            self.assertEqual(published_count, 1)
            tg_mock.assert_called_once()
            db.refresh(ai_article)
            db.refresh(fallback_article)
            db.refresh(proposal)
            self.assertEqual(ai_article.status, "published")
            self.assertIsNotNone(ai_article.published_at)
            self.assertIsInstance(ai_article.quiz, list)
            self.assertEqual(len(ai_article.quiz), 1)
            self.assertEqual(ai_article.quiz[0]["question"], "Sinov savoli?")
            self.assertEqual(proposal.status, "published")
            self.assertEqual(fallback_article.status, "pending")

    def test_pipeline_raises_when_all_topics_covered_and_rss_fails(self):
        with self.session_factory() as db:
            for index, (_, topic) in enumerate(LESSON_TOPICS):
                db.add(Article(
                    title=topic,
                    slug=f"covered-all-{index}",
                    original_title=topic,
                    original_url=f"internal://dars/covered-all-{index}",
                    source_name="Biznes Darslari",
                    status="published",
                ))
            db.commit()

        with (
            patch.object(pipeline, "engine", self.engine),
            patch.object(pipeline, "SessionLocal", self.session_factory),
            patch.object(pipeline, "RSS_IDEA_ENABLED", True),
            patch.object(
                pipeline,
                "create_weekly_proposals",
                side_effect=RuntimeError("Vertex AI billing required"),
            ),
        ):
            with self.assertRaises(RuntimeError):
                pipeline.run_pipeline()

        with self.session_factory() as db:
            latest_run = db.query(pipeline.PipelineRun).order_by(pipeline.PipelineRun.id.desc()).first()
            self.assertIsNotNone(latest_run)
            self.assertEqual(latest_run.status, "error")
            self.assertIn("Vertex AI billing required", latest_run.error)


class SuggestIdeasFallbackTests(unittest.TestCase):
    def test_vertex_failure_falls_back_to_gemini_when_api_key_set(self):
        signals = [
            {
                "id": 1,
                "source": "Example",
                "title": "Small business automation",
                "summary": "Summary",
                "published_at": None,
            }
        ]
        with (
            patch.object(rss_ideas, "AI_PROVIDER", "vertex"),
            patch.object(rss_ideas, "GEMINI_API_KEY", "test-key"),
            patch.object(
                rss_ideas,
                "_generate_with_vertex",
                side_effect=RuntimeError("Vertex AI 403 billing"),
            ),
            patch.object(
                rss_ideas,
                "_generate_with_gemini",
                return_value={"goyalar": [{"mavzu": "Zaxira g'oya"}]},
            ) as gemini_mock,
        ):
            ideas = rss_ideas.suggest_ideas(signals, [])

        gemini_mock.assert_called_once()
        self.assertEqual(ideas, [{"mavzu": "Zaxira g'oya"}])

    def test_vertex_failure_reraises_without_gemini_api_key(self):
        with (
            patch.object(rss_ideas, "AI_PROVIDER", "vertex"),
            patch.object(rss_ideas, "GEMINI_API_KEY", ""),
            patch.object(
                rss_ideas,
                "_generate_with_vertex",
                side_effect=RuntimeError("Vertex AI 403 billing"),
            ),
        ):
            with self.assertRaises(RuntimeError):
                rss_ideas.suggest_ideas([], [])

    def test_gemini_falls_back_to_next_model_on_503(self):
        class FakeResponse:
            def __init__(self, status_code, payload, text=""):
                self.status_code = status_code
                self._payload = payload
                self.text = text

            def json(self):
                return self._payload

        calls = []

        def fake_post(url, **kwargs):
            calls.append(url)
            if "gemini-3.8-flash" in url:
                return FakeResponse(503, {}, "High demand")
            return FakeResponse(
                200,
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {"text": '{"goyalar": [{"mavzu": "Model fallback g\'oya"}]}'}
                                ]
                            }
                        }
                    ]
                },
            )

        with (
            patch.object(rss_ideas, "GEMINI_API_KEY", "test-key"),
            patch.object(rss_ideas, "GEMINI_MODEL", "gemini-3.8-flash"),
            patch.object(
                rss_ideas,
                "GEMINI_FALLBACK_MODELS",
                ("gemini-4-hydrogen", "gemini-3.5-flash-lite"),
            ),
            patch.object(rss_ideas.httpx, "post", side_effect=fake_post),
        ):
            result = rss_ideas._generate_with_gemini("test")

        self.assertEqual(result, {"goyalar": [{"mavzu": "Model fallback g'oya"}]})
        self.assertEqual(len(calls), 2)
        self.assertIn("gemini-3.8-flash", calls[0])
        self.assertIn("gemini-4-hydrogen", calls[1])


if __name__ == "__main__":
    unittest.main()
