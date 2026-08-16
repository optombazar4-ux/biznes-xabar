from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class AdminLoginIn(BaseModel):
    token: str = Field(min_length=1, max_length=512)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    seo_title: str
    slug: str
    summary: str
    content: str
    practical_note: str
    tags: list
    quiz: list | None = None
    importance: int

    original_url: str
    source_name: str
    image_url: str | None
    category: CategoryOut | None
    status: str
    sent_to_telegram: bool
    published_at: datetime | None
    created_at: datetime

    @field_validator("quiz", mode="before")
    @classmethod
    def _normalize_quiz(cls, value: Any) -> Any:
        """Eski yozuvlarda `quiz` bitta obyekt bo'lishi mumkin.

        Bunday qiymat validatsiyani yiqitib, butun endpoint'ni 500 qilardi.
        Frontend faqat ro'yxatni ko'rsatgani uchun obyektni ro'yxatga o'raymiz.
        """
        if isinstance(value, dict):
            return [value]
        return value


class SitemapArticleOut(BaseModel):
    """Sitemap uchun kontent matnisiz yengil maqola yozuvi."""

    slug: str
    category_slug: str
    tags: list[str]
    published_at: datetime | None
    created_at: datetime


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    seo_title: str | None = Field(default=None, max_length=300)
    summary: str | None = None
    content: str | None = None
    practical_note: str | None = None
    tags: list[str] | None = None
    quiz: list[dict] | None = None
    importance: int | None = Field(default=None, ge=1, le=5)
    category_id: int | None = Field(default=None, ge=1)
    image_url: str | None = Field(default=None, max_length=1000)


class SubscribeIn(BaseModel):
    email: EmailStr


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
    created_at: datetime


class StatsOut(BaseModel):
    jami: int
    kutilmoqda: int
    chop_etilgan: int
    rad_etilgan: int
    telegramga_yuborilgan: int
    kategoriyalar_boyicha: dict
