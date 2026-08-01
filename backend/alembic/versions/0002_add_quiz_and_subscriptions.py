"""quiz va subscriptions qo'shish

Revision ID: 0002_add_quiz_and_subscriptions
Revises: 0001_initial_schema
Create Date: 2026-08-01 09:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002_add_quiz_and_subscriptions'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Article jadvaliga quiz ustunini qo'shish
    op.add_column('articles', sa.Column('quiz', sa.JSON(), nullable=True))

    # 2. Subscriptions jadvalini yaratish
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_email'), 'subscriptions', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_subscriptions_email'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_column('articles', 'quiz')
