"""Baza yetib bo'lmaganda ham servis ishga tusha olishi uchun testlar.

Render'da ishga tushirish buyrug'i `python -m app.migrate && uvicorn ...`
ko'rinishida. Migratsiya ulanish xatosida yiqilsa, `&&` zanjiri uzilib
butun servis ko'tarilmaydi — ya'ni tashqi baza uzilishi API'ni ham
o'ldiradi. Shuning uchun ulanish xatosi deployni to'xtatmasligi kerak.
"""
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app import migrate as migrate_module


UNREACHABLE_URL = "postgresql+psycopg2://nobody:x@127.0.0.1:1/none"


class MigrateResilienceTests(unittest.TestCase):
    def test_unreachable_database_does_not_raise(self):
        broken = create_engine(UNREACHABLE_URL)
        try:
            with patch.object(migrate_module, "engine", broken):
                migrate_module.migrate()  # xato tashlamasligi kerak
        finally:
            broken.dispose()

    def test_schema_errors_are_still_fatal(self):
        """Ulanish ishlab, sxema mos kelmasa — deploy to'xtashi kerak."""
        sqlite_engine = create_engine("sqlite:///:memory:")
        # Alembic izisiz, kutilmagan jadval: avtomatik stamp qilinmaydi.
        with sqlite_engine.connect() as connection:
            connection.exec_driver_sql("CREATE TABLE begona (id INTEGER PRIMARY KEY)")
            connection.commit()

        try:
            with patch.object(migrate_module, "engine", sqlite_engine):
                with self.assertRaises(RuntimeError):
                    migrate_module.migrate()
        finally:
            sqlite_engine.dispose()

    def test_operational_error_is_the_tolerated_case(self):
        """Ulanish xatosi aynan OperationalError sifatida keladi."""
        broken = create_engine(UNREACHABLE_URL)
        try:
            with self.assertRaises(OperationalError):
                with broken.connect():
                    pass
        finally:
            broken.dispose()


if __name__ == "__main__":
    unittest.main()
