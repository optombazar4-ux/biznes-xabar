import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import (
    FRONTEND_ORIGIN,
    MEDIA_DIR,
    RUN_BACKGROUND_SERVICES,
    validate_production_settings,
)
from .database import Base, SessionLocal, engine
from .models import Article, IdeaProposal, IdeaProposalRun
from .routers import admin, categories, news
from .seed import prune_legacy_content, seed_categories
from .pipeline import run_pipeline
from .bot.bot import main as run_bot
from .services.education import IDEA_TOPICS

PIPELINE_STATE = {
    "status": "not_started",
    "last_started_at": None,
    "last_completed_at": None,
    "last_error_at": None,
    "last_saved": None,
}


async def pipeline_loop_task():
    await asyncio.sleep(15)
    while True:
        PIPELINE_STATE["status"] = "running"
        PIPELINE_STATE["last_started_at"] = datetime.now(timezone.utc).isoformat()
        try:
            print("⏳ Running background lessons pipeline...")
            loop = asyncio.get_running_loop()
            saved = await loop.run_in_executor(None, run_pipeline)
            PIPELINE_STATE["status"] = "ok"
            PIPELINE_STATE["last_completed_at"] = datetime.now(timezone.utc).isoformat()
            PIPELINE_STATE["last_saved"] = saved
            print(f"✅ Pipeline done. Created {saved} lessons.")
        except Exception as e:
            PIPELINE_STATE["status"] = "error"
            PIPELINE_STATE["last_error_at"] = datetime.now(timezone.utc).isoformat()
            print(f"❌ Pipeline loop error: {e}")

        interval = int(os.getenv("PIPELINE_INTERVAL", "3600"))
        await asyncio.sleep(interval)


async def bot_task():
    await asyncio.sleep(5)
    try:
        print("🤖 Starting background Telegram Bot...")
        await run_bot()
    except Exception as e:
        print(f"❌ Telegram Bot error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_categories(db)
        prune_legacy_content(db)
    finally:
        db.close()
    
    bg_tasks = []
    if RUN_BACKGROUND_SERVICES:
        bg_tasks.append(asyncio.create_task(pipeline_loop_task()))
        if os.getenv("TELEGRAM_BOT_TOKEN"):
            bg_tasks.append(asyncio.create_task(bot_task()))
        else:
            print("⚠️ TELEGRAM_BOT_TOKEN is not set. Bot background task will not start.")
        
    yield
    
    for task in bg_tasks:
        task.cancel()
    if bg_tasks:
        await asyncio.gather(*bg_tasks, return_exceptions=True)


app = FastAPI(
    title="Biznes Darslari API",
    description="O'zbekistonda biznes ochish va yuritish bo'yicha amaliy darslar",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:3000",
        "https://biznesxabar.uz",
        "https://www.biznesxabar.uz",
    ],
    # Har qanday Vercel deploy (production + preview) domenini qabul qiladi
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(news.router)
app.include_router(categories.router)
app.include_router(admin.router)

# Generatsiya qilingan rasmlar (IMAGE_GENERATION=true rejimi uchun)
Path(MEDIA_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/")
def root():
    return {"loyiha": "Biznes Darslari", "hujjatlar": "/docs"}


@app.get("/health")
def health():
    db = SessionLocal()
    try:
        latest = db.query(Article).order_by(Article.created_at.desc()).first()
        latest_proposal_run = (
            db.query(IdeaProposalRun)
            .order_by(IdeaProposalRun.created_at.desc())
            .first()
        )
        return {
            "status": "ok",
            "database": "ok",
            "latest_article_at": latest.created_at if latest else None,
            "pipeline": PIPELINE_STATE,
            "idea_pipeline": {
                "curated_total": len(IDEA_TOPICS),
                "curated_published": (
                    db.query(Article)
                    .filter(Article.original_title.in_(IDEA_TOPICS))
                    .count()
                ),
                "approved_queue": (
                    db.query(IdeaProposal)
                    .filter(IdeaProposal.status == "approved")
                    .count()
                ),
                "latest_weekly_run": (
                    {
                        "status": latest_proposal_run.status,
                        "signals": latest_proposal_run.signals_count,
                        "suggestions": latest_proposal_run.suggestions_count,
                        "approved": latest_proposal_run.approved_count,
                        "created_at": latest_proposal_run.created_at,
                    }
                    if latest_proposal_run
                    else None
                ),
            },
        }
    finally:
        db.close()
