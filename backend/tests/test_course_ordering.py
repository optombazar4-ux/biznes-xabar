"""tartib=kurs uchun testlar.

Kurs tartibi kurikulumdagi mavzular ketma-ketligiga mos bo'lishi va
saralash bazada bajarilishi kerak — ilgari kategoriyadagi barcha maqola
to'liq matni bilan xotiraga yuklanardi.
"""
import unittest

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Article, Category
from app.routers.news import latest_lessons
from app.services.education import LESSON_TOPICS


class CourseOrderingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

        category = Category(name="Moliya", slug="moliya")
        self.db.add(category)
        self.db.flush()
        self.category = category

        # Kurikulumdan uchta mavzu — teskari tartibda kiritamiz
        self.topics = [topic for _, topic in LESSON_TOPICS[:3]]
        self.slug_by_topic = {}
        for i, topic in enumerate(reversed(self.topics)):
            slug = f"dars-{i}"
            self.slug_by_topic[topic] = slug
            self.db.add(Article(
                title=f"Dars {i}", slug=slug,
                original_url=f"internal://dars/{slug}",
                original_title=topic,
                status="published", category_id=category.id,
                content="Z" * 3000,
            ))
        # Kurikulumda yo'q mavzu — oxirida turishi kerak
        self.db.add(Article(
            title="Begona", slug="begona",
            original_url="internal://dars/begona",
            original_title="Kurikulumda yo'q mavzu",
            status="published", category_id=category.id,
            content="Z" * 3000,
        ))
        self.db.commit()

        self.statements = []
        event.listen(self.engine, "before_cursor_execute", self._record)

    def _record(self, conn, cursor, statement, params, context, executemany):
        self.statements.append(statement)

    def tearDown(self):
        event.remove(self.engine, "before_cursor_execute", self._record)
        self.db.close()
        self.engine.dispose()

    def _expected_slugs(self, topics):
        return [self.slug_by_topic[topic] for topic in topics]

    def test_lessons_follow_curriculum_order(self):
        lessons = latest_lessons(self.db, kategoriya="moliya", tartib="kurs", limit=100)

        self.assertEqual(
            [a["slug"] for a in lessons[:3]], self._expected_slugs(self.topics)
        )

    def test_unknown_topic_goes_last(self):
        lessons = latest_lessons(self.db, kategoriya="moliya", tartib="kurs", limit=100)

        self.assertEqual(lessons[-1]["slug"], "begona")

    def test_limit_and_offset_apply_in_curriculum_order(self):
        page = latest_lessons(
            self.db, kategoriya="moliya", tartib="kurs", limit=2, offset=1
        )

        self.assertEqual(
            [a["slug"] for a in page], self._expected_slugs(self.topics[1:3])
        )

    def test_content_is_not_fetched_but_reading_minutes_is_returned(self):
        lessons = latest_lessons(self.db, kategoriya="moliya", tartib="kurs", limit=1)

        self.assertNotIn("content", lessons[0])
        self.assertGreaterEqual(lessons[0]["reading_minutes"], 1)

    def test_query_fetches_only_requested_page(self):
        """Asosiy maqsad: saralash bazada, LIMIT so'rovning o'zida bo'lsin."""
        self.statements.clear()
        latest_lessons(self.db, kategoriya="moliya", tartib="kurs", limit=2)

        self.assertEqual(len(self.statements), 1)
        sql = self.statements[0].lower()
        self.assertIn("order by case", sql)
        self.assertIn("limit", sql)

    def test_default_order_is_newest_first_unchanged(self):
        lessons = latest_lessons(self.db, kategoriya="moliya", limit=100)

        self.assertEqual(len(lessons), 4)


if __name__ == "__main__":
    unittest.main()
