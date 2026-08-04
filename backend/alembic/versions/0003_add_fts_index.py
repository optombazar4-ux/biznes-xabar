"""PostgreSQL Full-Text Search (FTS) tezlashtirish — GIN indeksi

Revision ID: 0003_add_fts_index
Revises: 0002_add_quiz_and_subscriptions
Create Date: 2026-08-04 19:00:00.000000

news.py'dagi qidiruv so'rovida har safar tsvector qayta hisoblanadi.
Funksional GIN indeksi shu ifodani keshlaydi va katta bazada qidiruvni tezlashtiradi.
SQLite tsvector'ni qo'llab-quvvatlamagani uchun indeks faqat PostgreSQL'da yaratiladi.
"""
from typing import Sequence, Union

from alembic import op


revision: str = '0003_add_fts_index'
down_revision: Union[str, None] = '0002_add_quiz_and_subscriptions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# news.py'dagi ifoda bilan mutlaqo mos kelishi shart:
# to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(summary,'')
#             || ' ' || coalesce(content,'') || ' ' || coalesce(practical_note,''))
_SEARCH_TSV = (
    "to_tsvector('simple', "
    "coalesce(title, '') || ' ' || "
    "coalesce(summary, '') || ' ' || "
    "coalesce(content, '') || ' ' || "
    "coalesce(practical_note, ''))"
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # SQLite'da tsvector mavjud emas — indeks yaratilmaydi (xavfsiz o'tkazib yuboriladi)
        return
    op.execute(
        f"CREATE INDEX IF NOT EXISTS ix_articles_search_tsv "
        f"ON articles USING GIN ({_SEARCH_TSV})"
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("DROP INDEX IF EXISTS ix_articles_search_tsv")
