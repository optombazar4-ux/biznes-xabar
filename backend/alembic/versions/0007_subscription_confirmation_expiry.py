"""Expire pending newsletter confirmation links.

Revision ID: 0007_sub_confirm_expiry
Revises: 0006_rate_limit_buckets
Create Date: 2026-10-14 10:10:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0007_sub_confirm_expiry"
down_revision: Union[str, None] = "0006_rate_limit_buckets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column("confirmation_expires_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("subscriptions", "confirmation_expires_at")
