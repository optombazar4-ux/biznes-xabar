"""Persist content pipeline execution history.

Revision ID: 0004_add_pipeline_runs
Revises: 0003_add_fts_index
Create Date: 2026-08-17 10:15:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0004_add_pipeline_runs"
down_revision: Union[str, None] = "0003_add_fts_index"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trigger", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_count", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pipeline_runs_trigger", "pipeline_runs", ["trigger"])
    op.create_index("ix_pipeline_runs_status", "pipeline_runs", ["status"])
    op.create_index("ix_pipeline_runs_started_at", "pipeline_runs", ["started_at"])


def downgrade() -> None:
    op.drop_index("ix_pipeline_runs_started_at", table_name="pipeline_runs")
    op.drop_index("ix_pipeline_runs_status", table_name="pipeline_runs")
    op.drop_index("ix_pipeline_runs_trigger", table_name="pipeline_runs")
    op.drop_table("pipeline_runs")
