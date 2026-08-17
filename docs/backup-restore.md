# PostgreSQL backup va tiklash

`.github/workflows/database-backup.yml` har kuni PostgreSQL bazaning loyiha
ishlatadigan `public` sxemasini custom formatda eksport qiladi, alohida
PostgreSQL 17 bazasiga tiklab tekshiradi,
so‘ng faqat AES-256 bilan shifrlangan arxivni GitHub Actions artifact sifatida
30 kun saqlaydi.

## Bir martalik sozlash

GitHub repository `Settings → Secrets and variables → Actions` bo‘limida:

- `BACKUP_DATABASE_URL` — Supabase direct yoki session-pooler PostgreSQL URL;
- `BACKUP_ENCRYPTION_PASSWORD` — kamida 32 belgili tasodifiy, alohida sir.

Backup parolini parol menejerida saqlang. U yo‘qolsa arxivni tiklab bo‘lmaydi.

## Qo‘lda sinash

`Actions → Encrypted database backup → Run workflow` orqali ishga tushiring.
Workflow muvaffaqiyatli tugashi backup yaratilgani va bo‘sh test bazasiga
tiklana olganini bildiradi.

## Arxivni tiklash

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
  -in biznes-xabar-YYYY-MM-DD.dump.enc \
  -out biznes-xabar.dump

pg_restore --clean --if-exists --no-owner --no-acl \
  --dbname="$RESTORE_DATABASE_URL" biznes-xabar.dump
```

Avval yangi, bo‘sh test bazasiga tiklang. Production bazaga `--clean` bilan
tiklash mavjud obyektlarni o‘chiradi; uni faqat avariya tiklash rejasida va
alohida tasdiqdan keyin bajaring.
