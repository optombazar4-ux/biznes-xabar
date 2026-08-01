"""dastlabki sxema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-01 09:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=True)

    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('seo_title', sa.String(length=300), nullable=True),
        sa.Column('slug', sa.String(length=320), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('practical_note', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('importance', sa.Integer(), nullable=True),
        sa.Column('original_title', sa.String(length=500), nullable=True),
        sa.Column('original_url', sa.String(length=1000), nullable=False),
        sa.Column('source_name', sa.String(length=200), nullable=True),
        sa.Column('image_url', sa.String(length=1000), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('sent_to_telegram', sa.Boolean(), nullable=True),
        sa.Column('source_published_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_articles_original_url'), 'articles', ['original_url'], unique=True)
    op.create_index(op.f('ix_articles_slug'), 'articles', ['slug'], unique=True)
    op.create_index(op.f('ix_articles_status'), 'articles', ['status'], unique=False)

    op.create_table(
        'idea_proposals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('filters', sa.JSON(), nullable=True),
        sa.Column('source_urls', sa.JSON(), nullable=True),
        sa.Column('source_names', sa.JSON(), nullable=True),
        sa.Column('source_titles', sa.JSON(), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('estimated_budget_min', sa.Integer(), nullable=True),
        sa.Column('estimated_budget_max', sa.Integer(), nullable=True),
        sa.Column('risks', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        sa.Column('article_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('article_id')
    )
    op.create_index(op.f('ix_idea_proposals_status'), 'idea_proposals', ['status'], unique=False)
    op.create_index(op.f('ix_idea_proposals_title'), 'idea_proposals', ['title'], unique=True)

    op.create_table(
        'idea_proposal_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('signals_count', sa.Integer(), nullable=True),
        sa.Column('suggestions_count', sa.Integer(), nullable=True),
        sa.Column('approved_count', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_idea_proposal_runs_status'), 'idea_proposal_runs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('idea_proposal_runs')
    op.drop_table('idea_proposals')
    op.drop_table('articles')
    op.drop_table('categories')
