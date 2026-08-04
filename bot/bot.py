"""Biznes Darslari — yakka (standalone) Telegram bot ishga tushirgich.

Asosiy bot implementatsiyasi YAGONA joyda — `backend/app/bot/bot.py` da
saqlanadi. Ushbu fayl faqat uni mustaqil jarayon sifatida ishga tushiradi
(lokal ishlab chiqish yoki `docker compose --profile bot` uchun).

Ishga tushirish:  python bot.py
"""

import asyncio
import sys
from pathlib import Path

# Yagona implementatsiya joylashgan backend papkasini import yo'liga qo'shamiz.
# Repo ildizi: Path(__file__).resolve().parents[1]  (masalan .../biznes-xabar)
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# noqa: E402 — sys.path sozlanganidan keyin import qilinadi
from app.bot.bot import main  # noqa: E402

if __name__ == "__main__":
    asyncio.run(main())
