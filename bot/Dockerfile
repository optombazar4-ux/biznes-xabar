# Biznes Xabar — yakka (standalone) Telegram bot
# Build konteksti: repository ildizi (docker compose'da context: . sifatida).
# Botning yagona implementatsiyasi backend/app/bot/ da — shu sababli backend
# papkasi ham tasvirga ko'chiriladi.
FROM python:3.12-slim

WORKDIR /app

# Yakka bot uchun kerakli minimal bog'liqliklar
COPY bot/requirements.txt ./bot/requirements.txt
RUN pip install --no-cache-dir -r bot/requirements.txt

# Yagona bot implementatsiyasi (backend/app/bot/) va launcher (bot/)
COPY backend/app ./backend/app
COPY bot ./bot

CMD ["python", "bot/bot.py"]
