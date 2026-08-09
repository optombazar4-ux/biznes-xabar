"""
Biznes Darslari — Kunlik Avtomatik Kontent Generator & Pipeline Runner (Variant 2)
Ushbu skript har kuni 1 ta yangi dolzarb biznes darsini avtomatik yaratadi,
fallback-data.json faylini yangilaydi hamda IndexNow pinger va Telegram botini ishga tushiradi.
"""

import sys
import logging
from app.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    logging.info("🚀 Kunlik avtomatik kontent generatsiyasi boshlandi...")
    try:
        saved = run_pipeline()
        logging.info(
            "✅ Muvaffaqiyatli %s ta yangi biznes darsi yaratildi va "
            "indeksatsiyaga yuborildi!",
            saved,
        )
    except Exception as e:
        logging.error(f"❌ Kontent generatsiyasida xatolik: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
