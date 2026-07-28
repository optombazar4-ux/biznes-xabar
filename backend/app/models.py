from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    articles: Mapped[list["Article"]] = relationship(back_populates="category")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)

    # O'zbekcha kontent (AI agent tayyorlaydi)
    title: Mapped[str] = mapped_column(String(300))
    seo_title: Mapped[str] = mapped_column(String(300), default="")
    slug: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text, default="")           # qisqa xulosa
    content: Mapped[str] = mapped_column(Text, default="")           # to'liq maqola
    practical_note: Mapped[str] = mapped_column(Text, default="")    # "Bu nima degani?"
    tags: Mapped[list] = mapped_column(JSON, default=list)
    importance: Mapped[int] = mapped_column(Integer, default=3)      # 1-5

    # Asl manba
    original_title: Mapped[str] = mapped_column(String(500), default="")
    original_url: Mapped[str] = mapped_column(String(1000), unique=True, index=True)
    source_name: Mapped[str] = mapped_column(String(200), default="")
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    category: Mapped[Category | None] = relationship(back_populates="articles")

    # Holat oqimi: pending -> published (admin tasdiqlagach) yoki rejected
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    sent_to_telegram: Mapped[bool] = mapped_column(Boolean, default=False)

    source_published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IdeaProposal(Base):
    """RSS trendlari asosida AI taklif qilgan biznes g'oyasi auditi."""

    __tablename__ = "idea_proposals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    filters: Mapped[list] = mapped_column(JSON, default=list)
    source_urls: Mapped[list] = mapped_column(JSON, default=list)
    source_names: Mapped[list] = mapped_column(JSON, default=list)
    source_titles: Mapped[list] = mapped_column(JSON, default=list)
    rationale: Mapped[str] = mapped_column(Text, default="")
    estimated_budget_min: Mapped[int] = mapped_column(Integer, default=0)
    estimated_budget_max: Mapped[int] = mapped_column(Integer, default=0)
    risks: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="approved", index=True)
    validation_notes: Mapped[str] = mapped_column(Text, default="")
    article_id: Mapped[int | None] = mapped_column(
        ForeignKey("articles.id"), nullable=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class IdeaProposalRun(Base):
    """Haftalik taklif siklining holati va hisoboti."""

    __tablename__ = "idea_proposal_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    signals_count: Mapped[int] = mapped_column(Integer, default=0)
    suggestions_count: Mapped[int] = mapped_column(Integer, default=0)
    approved_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="running", index=True)
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
