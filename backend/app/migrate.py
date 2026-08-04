"""Deploy vaqtida yangi va avvaldan mavjud bazalarni xavfsiz migratsiya qiladi."""

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from .database import Base, engine
from . import models  # noqa: F401 - barcha metadata jadvallarini ro'yxatdan o'tkazadi


def _has_alembic_revision(table_names: set[str]) -> bool:
    if "alembic_version" not in table_names:
        return False
    with engine.connect() as connection:
        return bool(connection.execute(text("SELECT version_num FROM alembic_version")).first())


def _schema_contains_expected(inspector, expected_tables) -> bool:
    existing_tables = set(inspector.get_table_names())
    for table_name, expected_columns in expected_tables.items():
        if table_name not in existing_tables:
            return False
        actual_columns = {column["name"] for column in inspector.get_columns(table_name)}
        if not expected_columns.issubset(actual_columns):
            return False
    return True


def migrate() -> None:
    config = Config("alembic.ini")
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if _has_alembic_revision(table_names):
        command.upgrade(config, "head")
        return

    application_tables = table_names - {"alembic_version"}
    if not application_tables:
        command.upgrade(config, "head")
        return

    current_schema = {
        table.name: {column.name for column in table.columns}
        for table in Base.metadata.sorted_tables
    }
    if _schema_contains_expected(inspector, current_schema):
        command.stamp(config, "head")
        return

    revision_one_schema = {
        "categories": {"id", "name", "slug"},
        "articles": {
            "id", "title", "seo_title", "slug", "summary", "content",
            "practical_note", "tags", "importance", "original_title",
            "original_url", "source_name", "image_url", "category_id",
            "status", "sent_to_telegram", "source_published_at",
            "published_at", "created_at",
        },
        "idea_proposals": {"id", "title", "status", "article_id"},
        "idea_proposal_runs": {"id", "status", "created_at"},
    }
    article_columns = (
        {column["name"] for column in inspector.get_columns("articles")}
        if "articles" in table_names
        else set()
    )
    if (
        "quiz" not in article_columns
        and "subscriptions" not in table_names
        and _schema_contains_expected(inspector, revision_one_schema)
    ):
        command.stamp(config, "0001_initial_schema")
        command.upgrade(config, "head")
        return

    raise RuntimeError(
        "Bazadagi sxema kutilgan Alembic reviziyalariga mos emas. "
        "Avtomatik stamp qilinmadi; sxemani qo‘lda tekshirish kerak."
    )


if __name__ == "__main__":
    migrate()
