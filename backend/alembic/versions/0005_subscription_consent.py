"""Add confirmation and unsubscribe tokens for newsletter consent.

Revision ID: 0005_subscription_consent
Revises: 0004_add_pipeline_runs
Create Date: 2026-10-02 09:40:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0005_subscription_consent"
down_revision: Union[str, None] = "0004_add_pipeline_runs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subscriptions", sa.Column("confirmation_token", sa.String(128), nullable=True))
    op.add_column("subscriptions", sa.Column("unsubscribe_token", sa.String(128), nullable=True))
    op.add_column("subscriptions", sa.Column("confirmed_at", sa.DateTime(), nullable=True))
    op.create_index("ix_subscriptions_confirmation_token", "subscriptions", ["confirmation_token"], unique=True)
    op.create_index("ix_subscriptions_unsubscribe_token", "subscriptions", ["unsubscribe_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_subscriptions_unsubscribe_token", table_name="subscriptions")
    op.drop_index("ix_subscriptions_confirmation_token", table_name="subscriptions")
    op.drop_column("subscriptions", "confirmed_at")
    op.drop_column("subscriptions", "unsubscribe_token")
    op.drop_column("subscriptions", "confirmation_token")
