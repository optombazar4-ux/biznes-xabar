# Biznes Darslari

O‘zbekistonda biznes boshlash va yuritish bo‘yicha bepul amaliy darslar, biznes g‘oyalari va yordamchi vositalar platformasi.

## Imkoniyatlar

- Kurikulum asosida AI yordamida dars va biznes g‘oyalar yaratish
- Admin moderatsiyasi va muhimlik darajasiga asoslangan avtomatik chop etish
- Kategoriya, qidiruv, o‘xshash darslar va biznes g‘oya moslik testi
- Telegram kanal va bot integratsiyasi
- Email obuna va dayjest
- O‘zbekcha audio, RSS, sitemap, PWA va SEO metadata
- Supabase PostgreSQL yoki lokal SQLite

AI yordamida tayyorlangan kontent foydalanuvchiga ochiq ko‘rsatiladi. Soliq, huquq va moliya bo‘yicha muhim qarorlar rasmiy manbalar bilan tekshirilishi kerak.

## Arxitektura

```text
Next.js frontend ───────┐
Telegram bot ───────────┼── FastAPI API ── PostgreSQL
Admin panel ────────────┘        │
                                 ├── AI pipeline (Gemini / Vertex / Claude)
                                 ├── Telegram kanal
                                 ├── SMTP dayjest
                                 └── TTS audio/media
```

| Qism | Texnologiya | Papka |
|---|---|---|
| REST API va pipeline | FastAPI, SQLAlchemy, Alembic | `backend/` |
| Sayt va admin panel | Next.js 15, React 19, Tailwind CSS 4 | `frontend/` |
| Alohida Telegram bot | aiogram 3 | `bot/` |

## Docker bilan ishga tushirish

1. Muhit faylini tayyorlang:

```bash
cp .env.example .env
```

Kamida `ADMIN_TOKEN` va kerakli AI/Telegram kalitlarini to‘ldiring. `ADMIN_TOKEN` kamida 24 belgili tasodifiy qiymat bo‘lishi shart.

2. Stackni ishga tushiring:

```bash
docker compose up -d --build
```

Telegram bot boshqa serverda ishlayotgan bo‘lsa, lokal stack uni ishga tushirmaydi.
Botni ataylab lokal yoqish uchun:

```bash
docker compose --profile bot up -d bot
```

- Sayt: <http://localhost:3000>
- Admin: <http://localhost:3000/admin>
- API hujjatlari: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health> (yengil; batafsil holat — `/health/details`)
- Pipeline monitor: <http://localhost:8000/health/pipeline> (stale/error holatda HTTP 503)

Backend container ishga tushishidan oldin `python -m app.migrate` orqali Alembic migratsiyasini xavfsiz bajaradi. Pipeline backend sog‘lom bo‘lgandan keyin boshlanadi.

## Docker’siz lokal ishga tushirish

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m app.migrate
uvicorn app.main:app --reload
```

Backend loyiha ildizidagi `.env` faylini ham o‘qiydi. `DATABASE_URL` berilmasa `backend/biznesxabar.db` SQLite bazasi ishlatiladi.

Pipeline’ni bir marta qo‘lda ishga tushirish:

```bash
python -m app.pipeline
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### Telegram bot

```bash
cd bot
pip install -r requirements.txt
python bot.py
```

## Muhim konfiguratsiyalar

| O‘zgaruvchi | Standart | Vazifasi |
|---|---:|---|
| `DATABASE_URL` | SQLite | PostgreSQL/SQLite ulanishi |
| `ADMIN_TOKEN` | yo‘q | Admin login siri; kamida 24 belgi |
| `JWT_SECRET_KEY` | `ADMIN_TOKEN` | Ixtiyoriy alohida JWT siri |
| `AI_PROVIDER` | `gemini` | `gemini`, `vertex` yoki `claude` |
| `AUTO_PUBLISH` | `true` | Mos darslarni avtomatik chop etish |
| `AUTO_PUBLISH_MIN_IMPORTANCE` | `1` | Avto-chop uchun minimal baho |
| `AUTO_TELEGRAM` | `true` | Chop etilgan muhim darslarni yuborish |
| `AUTO_TELEGRAM_MIN_IMPORTANCE` | `4` | Telegram uchun minimal baho |
| `RUN_BACKGROUND_SERVICES` | `true` | API jarayonida pipeline/botni yuritish |
| `PIPELINE_STALE_MINUTES` | `120` | Pipeline monitor uchun eskirish chegarasi |
| `PIPELINE_ALERT_WEBHOOK_URL` | yo‘q | Pipeline xatosida JSON alert qabul qiluvchi webhook |
| `FRONTEND_ORIGIN` | `http://localhost:3000` | Kanonik frontend manzili |
| `CORS_ORIGINS` | `FRONTEND_ORIGIN` | Vergul bilan ajratilgan ruxsatli originlar |
| `BACKEND_PUBLIC_URL` | `http://localhost:8000` | Media fayllarning tashqi API manzili |

Barcha mavjud parametrlar `.env.example` faylida ko‘rsatilgan.

## Asosiy API endpointlar

### Ommaviy

| Metod | Yo‘l | Vazifasi |
|---|---|---|
| GET | `/api/news` | Chop etilgan darslar |
| GET | `/api/news/search?q=` | Qidiruv |
| GET | `/api/news/trends` | Ommabop teglar |
| GET | `/api/news/rss` | RSS feed |
| GET | `/api/news/{slug}` | Bitta dars |
| GET | `/api/news/{slug}/related` | O‘xshash darslar |
| GET | `/api/news/{slug}/audio` | Keshlangan/TTS audio |
| GET | `/api/news/ideas/match` | Mezonga mos biznes g‘oyalari |
| POST | `/api/news/subscribe` | Email obuna |
| GET | `/api/categories` | Kategoriyalar |

### Admin

`POST /api/admin/login` admin tokenni tekshiradi va JWT qaytaradi. Qolgan admin endpointlari `Authorization: Bearer <jwt>` talab qiladi.

- `GET /api/admin/articles`
- `PUT /api/admin/articles/{id}`
- `POST /api/admin/articles/{id}/approve`
- `POST /api/admin/articles/{id}/reject`
- `POST /api/admin/articles/{id}/telegram`
- `DELETE /api/admin/articles/{id}`
- `POST /api/admin/send-digest`
- `GET /api/admin/stats`

Admin token frontend bundle’da saqlanmaydi. JWT faqat brauzer sessiyasi davomida `sessionStorage`da turadi.

## Test va tekshiruvlar

```bash
cd backend
python -m pytest -q
python -m compileall -q app

cd ../frontend
npm run build
npm audit --omit=dev

cd ..
docker compose config --quiet
```

## Zaxira va monitoring

- `/health/pipeline` oxirgi pipeline ishini bazadagi doimiy auditdan tekshiradi.
- Pipeline xatosida `PIPELINE_ALERT_WEBHOOK_URL` ga maxfiy ma’lumotsiz JSON yuboriladi.
- Kunlik shifrlangan PostgreSQL backup va restore sinovi
  `.github/workflows/database-backup.yml` da.
- Bir martalik sozlash va tiklash yo‘riqnomasi: `docs/backup-restore.md`.

## Deploy

- `render.yaml` backend, pipeline va botni bitta Render web-service jarayonida yuritish uchun sozlangan.
- `frontend/vercel.json` frontendni Vercel’da joylashtirish uchun ishlatiladi.
- Render’da `DATABASE_URL`, `ADMIN_TOKEN`, `BACKEND_PUBLIC_URL` va AI/Telegram sirlarini alohida kiriting.
- Vercel’da `NEXT_PUBLIC_API_URL` backendning HTTPS manziliga teng bo‘lishi kerak.

Sirlarni Git’ga commit qilmang. `.env`, service-account JSON va lokal bazalar `.gitignore` orqali chiqarib tashlangan.
