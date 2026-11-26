"""Quiz normalizatsiyasi va AI zaxira shabloni xulq-atvori uchun testlar.

Ikki kafolat tekshiriladi:
1. `quiz` doimo frontend kutgan ro'yxat ko'rinishida bo'ladi (LessonQuiz faqat
   massivni ko'rsatadi).
2. AI javob bermay zaxira shablon qaytganda dars saytga avtomatik chiqmaydi.
"""
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import pipeline
from app.database import Base
from app.models import Article, Category
from app.schemas import ArticleOut
from app.services import education


VALID_QUESTION = {
    "question": "Tannarx nima?",
    "options": ["Sof foyda", "Mahsulot ishlab chiqarish xarajati", "Aylanma", "Soliq"],
    "answer_index": 1,
    "explanation": "Tannarx — mahsulotni tayyorlash uchun ketgan xarajat.",
}


class CleanQuizTests(unittest.TestCase):
    def test_single_dict_is_wrapped_into_list(self):
        cleaned = education._clean_quiz(dict(VALID_QUESTION))

        self.assertIsInstance(cleaned, list)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["question"], VALID_QUESTION["question"])
        self.assertEqual(cleaned[0]["answer_index"], 1)

    def test_valid_list_is_preserved(self):
        cleaned = education._clean_quiz([VALID_QUESTION, VALID_QUESTION])

        self.assertEqual(len(cleaned), 2)

    def test_malformed_questions_are_dropped(self):
        cleaned = education._clean_quiz([
            {**VALID_QUESTION, "question": "   "},          # savol matni yo'q
            {**VALID_QUESTION, "options": ["Bitta variant"]},  # variant yetarli emas
            {**VALID_QUESTION, "answer_index": 9},           # indeks chegaradan tashqarida
            {**VALID_QUESTION, "answer_index": "1"},         # indeks butun son emas
            "savol emas",
            VALID_QUESTION,
        ])

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["question"], VALID_QUESTION["question"])

    def test_none_and_garbage_return_empty_list(self):
        self.assertEqual(education._clean_quiz(None), [])
        self.assertEqual(education._clean_quiz("quiz"), [])


class CuratedFallbackTests(unittest.TestCase):
    def test_fallback_quiz_is_a_list(self):
        result = education._generate_curated_fallback("Tannarxni hisoblash")

        self.assertIsInstance(result["quiz"], list)
        self.assertEqual(len(result["quiz"]), 1)
        self.assertIn("question", result["quiz"][0])

    def test_fallback_is_flagged(self):
        result = education._generate_curated_fallback("Tannarxni hisoblash")

        self.assertTrue(education.is_fallback(result))

    def test_ai_result_is_not_flagged(self):
        self.assertFalse(education.is_fallback({"sarlavha": "Dars", "quiz": []}))

    def test_generate_lesson_without_api_key_returns_flagged_list_quiz(self):
        with (
            patch.object(education, "AI_PROVIDER", "gemini"),
            patch.object(education, "GEMINI_API_KEY", ""),
        ):
            result = education.generate_lesson("Tannarxni hisoblash")

        self.assertTrue(education.is_fallback(result))
        self.assertIsInstance(result["quiz"], list)
        self.assertEqual(len(result["quiz"]), 1)


class ArticleOutQuizTests(unittest.TestCase):
    """Eski yozuvlardagi obyekt-quiz javob validatsiyasini yiqitmasligi kerak."""

    BASE = {
        "id": 1,
        "title": "Dars",
        "seo_title": "Dars",
        "slug": "dars",
        "summary": "Xulosa",
        "content": "Matn",
        "practical_note": "Amaliy",
        "tags": ["moliya"],
        "importance": 3,
        "original_url": "internal://dars/dars",
        "source_name": "Biznes Darslari",
        "image_url": None,
        "category": None,
        "status": "published",
        "sent_to_telegram": False,
        "published_at": None,
        "created_at": "2026-01-01T00:00:00",
    }

    def test_legacy_dict_quiz_is_wrapped(self):
        out = ArticleOut(**{**self.BASE, "quiz": VALID_QUESTION})

        self.assertEqual(out.quiz, [VALID_QUESTION])

    def test_list_quiz_passes_through(self):
        out = ArticleOut(**{**self.BASE, "quiz": [VALID_QUESTION]})

        self.assertEqual(out.quiz, [VALID_QUESTION])

    def test_missing_quiz_is_none(self):
        self.assertIsNone(ArticleOut(**self.BASE).quiz)


class FallbackIsNotAutoPublishedTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

        category = Category(name="Moliya", slug="moliya")
        self.db.add(category)
        self.db.commit()
        self.categories = {"moliya": category}

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _create(self, lesson):
        with (
            patch.object(pipeline, "generate_lesson", return_value=lesson),
            patch.object(pipeline, "AUTO_PUBLISH", True),
            patch.object(pipeline, "AUTO_PUBLISH_MIN_IMPORTANCE", 1),
        ):
            return pipeline._create_lesson(
                self.db, self.categories, "moliya", "Tannarxni hisoblash"
            )

    def test_fallback_lesson_stays_pending(self):
        article = self._create(education._generate_curated_fallback("Tannarxni hisoblash"))

        self.assertIsNotNone(article)
        self.assertEqual(article.status, "pending")
        self.assertIsNone(article.published_at)

    def test_real_ai_lesson_is_published(self):
        lesson = {
            "sarlavha": "Tannarxni to'g'ri hisoblash",
            "seo_sarlavha": "Tannarx hisobi",
            "xulosa": "Qisqacha",
            "maqola": "## Matn",
            "amaliy_ahamiyat": "Bugun hisoblang",
            "teglar": ["moliya"],
            "quiz": [VALID_QUESTION],
        }

        article = self._create(lesson)

        self.assertIsNotNone(article)
        self.assertEqual(article.status, "published")
        self.assertIsNotNone(article.published_at)


class ExtractResponseTextTests(unittest.TestCase):
    def test_skips_thought_parts_and_returns_actual_text(self):
        payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"thought": True, "text": "ichki mulohaza"},
                            {"text": '{"sarlavha": "Dars"}'},
                        ]
                    }
                }
            ]
        }
        self.assertEqual(
            education._extract_response_text(payload),
            '{"sarlavha": "Dars"}',
        )


class VertexFallbackTests(unittest.TestCase):
    def test_vertex_failure_falls_back_to_gemini_when_api_key_set(self):
        with (
            patch.object(education, "AI_PROVIDER", "vertex"),
            patch.object(education, "GEMINI_API_KEY", "test-key"),
            patch.object(
                education,
                "_generate_with_vertex",
                side_effect=RuntimeError("Vertex AI 403"),
            ),
            patch.object(
                education,
                "_generate_with_gemini",
                return_value={"sarlavha": "Gemini natija"},
            ) as gemini_mock,
        ):
            result = education._call_ai_provider("Mavzu")

        gemini_mock.assert_called_once_with("Mavzu", None)
        self.assertEqual(result, {"sarlavha": "Gemini natija"})

    def test_vertex_failure_reraises_without_gemini_api_key(self):
        with (
            patch.object(education, "AI_PROVIDER", "vertex"),
            patch.object(education, "GEMINI_API_KEY", ""),
            patch.object(
                education,
                "_generate_with_vertex",
                side_effect=RuntimeError("Vertex AI 403"),
            ),
        ):
            with self.assertRaises(RuntimeError):
                education._call_ai_provider("Mavzu")


class GeminiModelFallbackTests(unittest.TestCase):
    def test_falls_back_to_next_model_on_503(self):
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
                        {"content": {"parts": [{"text": '{"sarlavha": "Zaxira model darsi"}'}]}}
                    ]
                },
            )

        with (
            patch.object(education, "GEMINI_API_KEY", "test-key"),
            patch.object(education, "GEMINI_MODEL", "gemini-3.8-flash"),
            patch.object(
                education,
                "GEMINI_FALLBACK_MODELS",
                ("gemini-4-hydrogen", "gemini-3.5-flash-lite"),
            ),
            patch.object(education.httpx, "post", side_effect=fake_post),
        ):
            result = education._generate_with_gemini("Mavzu")

        self.assertEqual(result, {"sarlavha": "Zaxira model darsi"})
        self.assertEqual(len(calls), 2)
        self.assertIn("gemini-3.8-flash", calls[0])
        self.assertIn("gemini-4-hydrogen", calls[1])


if __name__ == "__main__":
    unittest.main()
