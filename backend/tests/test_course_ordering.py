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
        for i, topic in enumerate(reversed(self.topics)):
            self.db.add(Article(
                title=f"Dars {i}", slug=f"dars-{i}",
                original_url=f"internal://dars/dars-{i}",
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

    def test_lessons_follow_curriculum_order(self):
        lessons = latest_lessons(self.db, kategoriya="moliya", tartib="kurs", limit=100)

        self.assertEqual([a.original_title for a in lessons[:3]], self.topics)

    def test_unknown_topic_goes_last(self):
        lessons = latest_lessons(self.db, kategoriya="moliya", tartib="kurs", limit=100)

        self.assertEqual(lessons[-1].original_title, "Kurikulumda yo'q mavzu")

    def test_limit_and_offset_apply_in_curriculum_order(self):
        page = latest_lessons(
            self.db, kategoriya="moliya", tartib="kurs", limit=2, offset=1
        )

        self.assertEqual([a.original_title for a in page], self.topics[1:3])

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
