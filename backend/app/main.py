import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

# Strukturalangan loglar: vaqt + daraja + modul + xabar.
# LOG_LEVEL=DEBUG bilan batafsil, INFO (standart) bilan yetarli darajada.
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# httpx INFO yozuvlari so'ralgan URL'ni to'liq chiqaradi. Telegram Bot API
# tokeni URL yo'lida bo'lgani uchun uni production loglariga sizdirmaymiz.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("biznesdarslari")


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text

from .config import (
    BACKEND_PUBLIC_URL,
    CORS_ORIGINS,
    MEDIA_DIR,
    RUN_BACKGROUND_SERVICES,
    validate_production_settings,
)
from .database import SessionLocal
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
            logger.info("Running background lessons pipeline...")
            loop = asyncio.get_running_loop()
            saved = await loop.run_in_executor(None, run_pipeline)
            PIPELINE_STATE["status"] = "ok"
            PIPELINE_STATE["last_completed_at"] = datetime.now(timezone.utc).isoformat()
            PIPELINE_STATE["last_saved"] = saved
            logger.info("Pipeline done. Created %s lessons.", saved)
        except Exception as e:
            PIPELINE_STATE["status"] = "error"
            PIPELINE_STATE["last_error_at"] = datetime.now(timezone.utc).isoformat()
            logger.exception("Pipeline loop error: %s", e)

        interval = int(os.getenv("PIPELINE_INTERVAL", "3600"))
        await asyncio.sleep(interval)


async def bot_task():
    await asyncio.sleep(5)
    try:
        logger.info("Starting background Telegram Bot...")
        await run_bot()
    except Exception as e:
        logger.exception("Telegram Bot error: %s", e)


async def keep_alive_task():
    """Render'da backend uxlab qolmasligi uchun har 5 daqiqada self-ping.

    Faqat o'z /health manzili so'raladi. Frontend (Vercel) uxlamaydi, uni
    ping qilish esa har safar bosh sahifaning barcha API chaqiruvlarini,
    demak bazaga so'rovlarni ishga tushirardi — kuniga 288 marta, birorta
    ham real tashrifchisiz. Shuning uchun u ro'yxatdan olib tashlandi.
    """
    await asyncio.sleep(10)
    import httpx

    url = f"{BACKEND_PUBLIC_URL.rstrip('/')}/health"
    if not url.startswith("http"):
        logger.warning("BACKEND_PUBLIC_URL noto'g'ri — keep-alive ishga tushmadi.")
        return

    logger.info("Anti-Sleep (Keep-Alive Heartbeat) service started.")
    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            await asyncio.sleep(300)  # 5 daqiqa
            try:
                await client.get(url)
            except Exception:
                pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    # Baza yetib bo'lmasa ham API ko'tarilsin — aks holda tashqi baza uzilishi
    # butun servisni yiqitadi. Holat /health orqali "degraded" deb ko'rinadi.
    try:
        db = SessionLocal()
        try:
            seed_categories(db)
            prune_legacy_content(db)
        finally:
            db.close()
    except Exception as error:
        logger.warning(
            "Boshlang'ich seed/prune bajarilmadi (%s). API baribir ishga tushadi.",
            type(error).__name__,
        )


    bg_tasks = []
    if RUN_BACKGROUND_SERVICES:
        bg_tasks.append(asyncio.create_task(pipeline_loop_task()))
        bg_tasks.append(asyncio.create_task(keep_alive_task()))
        if os.getenv("TELEGRAM_BOT_TOKEN"):
            bg_tasks.append(asyncio.create_task(bot_task()))
        else:
            logger.warning("TELEGRAM_BOT_TOKEN is not set. Bot background task will not start.")
        
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
        origin.strip()
        for origin in CORS_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(categories.router)
app.include_router(admin.router)

# Generatsiya qilingan rasmlar va audiorasmlar
Path(MEDIA_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")



@app.get("/")
def root():
    return {"loyiha": "Biznes Darslari", "hujjatlar": "/docs"}


@app.get("/health")
def health():
    """Yengil sog'liq tekshiruvi — Render va keep-alive buni muntazam chaqiradi.

    Ilgari bu yerda bir necha COUNT va 100 elementli IN so'rovi bajarilardi,
    ya'ni har bir tekshiruv bepul tarifdagi baza trafigini behuda sarflardi.
    Endi faqat bitta arzon SELECT 1 bilan ulanish tekshiriladi; kontent
    statistikasi /health/details ga ko'chirildi.

    Baza ishlamaganda ham 200 qaytariladi ("degraded"), chunki qayta ishga
    tushirish tashqi baza muammosini hal qilmaydi — faqat restart siklini
    keltirib chiqaradi.
    """
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception as error:
        logger.warning("Health check DB xatosi: %s", type(error).__name__)
        database = "error"
    finally:
        db.close()

    return {
        "status": "ok" if database == "ok" else "degraded",
        "database": database,
        "pipeline": PIPELINE_STATE,
    }


@app.get("/health/details")
def health_details():
    """Kontent quvuri bo'yicha batafsil holat — qo'lda tekshirish uchun.

    Bir necha COUNT bajaradi, shuning uchun avtomatik monitoring emas,
    faqat kerak bo'lganda chaqirilishi ko'zda tutilgan.
    """
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
