# Biznes Xabar — AI agent uchun handoff

Yangilangan: 2026-08-04, Asia/Tashkent.

Bu fayl boshqa AI agent loyihani kontekstsiz davom ettira olishi uchun yozildi. Maxfiy tokenlar va parollar bu faylga ataylab kiritilmagan.

## 1. Hozirgi holat

- Repository: `https://github.com/optombazar4-ux/biznes-xabar`
- Aktiv branch: `main`
- Production commit: `6b2eba203211550d1b75a1747e4a711bb28dd3a1`
- Commit nomi: `feat: harden production deployment and content pipeline`
- Worktree tekshiruv vaqtida toza edi.
- Feature branch saqlanib qolgan: `codex/production-readiness`.
- Render backend: `https://biznes-xabar-backend.onrender.com`
- Render service ID: `srv-d96sond8nd3s73bklo50`
- Render Blueprint ID: `exs-d96soi58nd3s73bkl920`
- Production frontend: `https://biznesdarslari.uz`
- Eski Vercel URL `https://biznes-xabar.vercel.app` production domenga `307` redirect qiladi.

Render deploy muvaffaqiyatli yakunlangan. Start command:

```text
python -m app.migrate && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Alembic migratsiyasi PostgreSQL bazada bajarilgan va servis `live` holatga chiqqan.

## 2. Oxirgi tekshiruv natijalari

- `GET /health` → `200`
- Database → `ok`
- Pipeline → `ok`
- `GET /api/news?limit=1` → `200`
- `GET /api/admin/stats` autentifikatsiyasiz → `401` (kutilgan natija)
- Frontend final URL → `https://biznesdarslari.uz/`, status `200`
- Admin frontend → `https://biznesdarslari.uz/admin`, status `200`
- Backend testlari: `18/18` o‘tgan.
- Frontend production build o‘tgan.
- `npm audit`: `0` vulnerability.
- Lokal Docker stack ishlayapti:
  - backend: `localhost:8000`, healthy
  - frontend: `localhost:3000`
  - PostgreSQL: healthy
  - pipeline: running
  - alohida bot container ataylab ishga tushirilmagan

Oxirgi production pipeline run:

- Boshlangan: `2026-08-04T04:03:08Z` (`09:03` Tashkent)
- Tugagan: `2026-08-04T04:03:11Z`
- Xato: yo‘q
- Yaratilgan yangi dars: `0`

## 3. Avtomatik kontent va Telegram holati

Production sozlamalari:

- `RUN_BACKGROUND_SERVICES=true`
- `AUTO_PUBLISH=true`
- `AUTO_TELEGRAM=true`
- `AUTO_TELEGRAM_MIN_IMPORTANCE=4`
- `PIPELINE_INTERVAL=3600`
- Telegram kanal: `@biznesxabari`

Ishlash tartibi:

1. Pipeline servis ishga tushgandan 15 soniya keyin ishlaydi.
2. Keyin har 3600 soniyada qayta ishlaydi.
3. Faqat yangi maqola/dars yaratilsa va u `published` bo‘lsa keyingi bosqichga o‘tadi.
4. Telegram token mavjud va importance kamida `4` bo‘lsa kanalga yuboriladi.
5. Importance `3` bo‘lgan yoki yangi kontent yaratilmagan run Telegram xabari chiqarmaydi.

Deploy almashinuvi vaqtida bitta `TelegramConflictError` qayd etilgan. Keyingi loglarda u takrorlanmagan. Bu eski va yangi Render instansiyasi bir necha soniya parallel ishlagani bilan izohlanadi.

Muhim: production bot ishlayotgan paytda lokal botni yoki `docker compose --profile bot ...` ni ishga tushirmang. Aks holda Telegram long-polling konflikti qaytadi.

## 4. P0 — zudlik bilan bajariladigan xavfsizlik ishlari

### 4.1. GitHub PAT’ni almashtirish

Oldin `.git/config` remote URL ichida GitHub PAT bo‘lgan. U olib tashlangan va remote hozir xavfsiz ko‘rinishda:

```text
https://github.com/optombazar4-ux/biznes-xabar.git
```

Lekin eski PAT kompromat bo‘lgan deb hisoblanishi kerak:

1. GitHub Settings → Developer settings orqali eski PAT’ni revoke qiling.
2. GitHub CLI/keyring loginidan foydalaning.
3. Tokenni URL, commit, log yoki `.md` faylga yozmang.

### 4.2. `ADMIN_TOKEN`ni almashtirish

Eski public Git commit message’larida admin token matni ko‘rinib qolgan. Shu sabab Render Environment’dagi `ADMIN_TOKEN` albatta yangi, tasodifiy kuchli qiymatga almashtirilsin.

- Yangi qiymatni chatga yoki repositoryga yozmang.
- Admin panelga kirish jarayonini yangi token bilan tekshiring.
- Git tarixini rewrite qilish faqat foydalanuvchi alohida tasdiqlasa bajarilsin; avval tokenni rotate qilish yetakchi vazifa.

### 4.3. Render Deploy Hook’ni regeneratsiya qilish

Render Settings sahifasidagi private deploy hook avval diagnostika chiqishida ko‘ringan. Uni kompromat deb hisoblab, Render’da `Regenerate hook` qiling. Yangi URL’ni hech qayerga chop etmang.

## 5. P0 — production origin/CORS tuzatishi

`render.yaml` hozir frontend origin sifatida eski Vercel URL’ni ishlatadi:

```yaml
FRONTEND_ORIGIN: https://biznes-xabar.vercel.app
CORS_ORIGINS: https://biznes-xabar.vercel.app
SITE_URL: https://biznes-xabar.vercel.app
```

Amaldagi production domen esa `https://biznesdarslari.uz`.

Keyingi agent quyidagini bajarishi kerak:

1. `render.yaml` ichida `FRONTEND_ORIGIN` va `SITE_URL`ni `https://biznesdarslari.uz` ga o‘zgartiring.
2. `CORS_ORIGINS`ga kamida `https://biznesdarslari.uz` ni qo‘shing. Zarur bo‘lsa Vercel originni ham vergul bilan saqlang.
3. Backend CORS preflight’ini custom domendan tekshiring.
4. Commit → push → Render Blueprint sync/deploy.
5. Deploydan so‘ng admin panel va public frontend orqali real API requestlarni tekshiring.

## 6. P1 — avtomatik Telegram’ni end-to-end tekshirish

Keyingi soatlik pipeline runni Render loglarida kuzating. Tekshiriladigan yozuvlar:

```text
Running background lessons pipeline...
Pipeline done. Created N lessons.
Telegram kanalga yuborildi
```

Agar `Created 0 lessons` bo‘lsa, Telegram chiqmasligi normal.

Live kanalga test xabar yuborish tashqi ta’sirli amal. Foydalanuvchidan alohida ruxsat olmasdan test post yubormang. Ruxsat berilsa:

1. Test uchun importance `4` yoki `5` bo‘lgan bitta maqola yarating/tanlang.
2. Aynan bir marta yuboring.
3. `sent_to_telegram=true` bo‘lganini bazadan yoki admin API orqali tekshiring.
4. Takroriy yuborish bo‘lmasligini tasdiqlang.

## 7. P1 — Vercel deployni commit darajasida tasdiqlash

Frontend URL ishlayapti, lekin Vercel production deployment aynan `6b2eba2` commitidan qurilgani hali tekshirilmagan.

1. Vercel dashboard yoki CLI’da production deployment commitini tekshiring.
2. Agar eski commit bo‘lsa, `main` branchdan yangi production deploy qiling.
3. Quyidagilarni browser orqali tekshiring:
   - bosh sahifa;
   - maqola sahifasi;
   - admin login;
   - `LessonComments`;
   - `SmartMatcher`;
   - subscribe popup;
   - browser console va network xatolari.

## 8. P1 — background job ishonchliligi

Backend Render Free web service ichida pipeline, Telegram bot va keep-alive bir processda ishlayapti. Kod har 5 daqiqada backend va frontendga heartbeat yuboradi, lekin Free plan uchun 24/7 background ishga mutlaq kafolat yo‘q.

Barqaror production uchun variantlardan birini tanlang:

- Render paid instance;
- alohida background worker;
- Render Cron Job;
- GitHub Actions cron yoki boshqa scheduler.

Tanlovdan oldin xarajat va Telegram botning faqat bitta instansiyada ishlash talabini foydalanuvchi bilan kelishing.

## 9. P2 — texnik qarz va kuzatuv

1. Render logida Python `3.14.3` default ishlatilgan. Production runtime’ni qo‘llab-quvvatlanadigan aniq Python versiyasiga pin qilishni ko‘rib chiqing.
2. Pipeline va Telegram uchun structured logging/alert qo‘shing.
3. `/health` orqali `last_started_at`, `last_completed_at`, `last_error_at`, `last_saved` ni monitoring qiling.
4. Bir necha ketma-ket run `Created 0 lessons` bo‘lsa, RSS/AI provider limitlari va kontent deduplikatsiyasini diagnostika qiling.
5. Remote/local `codex/production-readiness` branchini faqat foydalanuvchi tasdig‘i bilan keyin tozalash mumkin.

## 10. Muhim fayllar

- `render.yaml` — Render servis va environment konfiguratsiyasi.
- `backend/app/main.py` — pipeline, Telegram bot va keep-alive background tasklar.
- `backend/app/pipeline.py` — auto-publish va Telegram yuborish shartlari.
- `backend/app/config.py` — environment qiymatlari va production validation.
- `backend/app/migrate.py` — deploy vaqtida Alembic migratsiyasi.
- `backend/app/rate_limit.py` — rate limiting.
- `backend/app/deps.py` — admin/JWT autentifikatsiyasi.
- `backend/tests/test_security_and_policies.py` — xavfsizlik va policy testlari.
- `frontend/app/admin/page.js` — admin interfeys.
- `frontend/lib/api.js` — frontend API konfiguratsiyasi.
- `docker-compose.yml` — lokal servislar; bot alohida profile’da.
- `README.md` — lokal ishga tushirish va deploy ko‘rsatmalari.

## 11. Agent ishni boshlaganda bajaradigan qisqa checklist

```text
[ ] git status va HEAD=6b2eba2 ekanini tekshir
[ ] Hech qanday secretni chiqarmasdan Render/GitHub auth holatini tekshir
[ ] GitHub PAT, ADMIN_TOKEN va Render deploy hook rotationini yakunla
[ ] Production origin/CORS qiymatlarini biznesdarslari.uz uchun tuzat
[ ] Test/buildni qayta bajar
[ ] Feature branchda commit qil va tasdiqlangan push/deploy jarayonini bajar
[ ] Render migratsiya, live status va /health=200 ni tekshir
[ ] Vercel deployment commitini tasdiqla
[ ] Keyingi pipeline run va Telegram loglarini kuzat
[ ] Natijani foydalanuvchiga secretlarsiz hisobot qil
```

## 12. Ehtiyotkorlik qoidalari

- `.env`, Render Environment yoki GitHub credential qiymatlarini terminal/chatga chiqarmang.
- Live Telegram kanalga foydalanuvchi ruxsatisiz test xabar yubormang.
- Git tarixini rewrite, branch delete yoki servis delete kabi destruktiv amallarni alohida tasdiqsiz bajarmang.
- Production bot ishlayotganida ikkinchi polling bot instansiyasini yoqmang.
- Render/Vercel’da o‘zgarishdan oldin aniq service/project va branchni tekshiring.
