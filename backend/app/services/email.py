"""Email tasdiqlashi va dayjestlarini SMTP orqali yuborish."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from typing import Mapping, Sequence

from ..config import FRONTEND_ORIGIN

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@biznesdarslari.uz")


def _smtp_is_configured() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def _send_html_email(to_email: str, subject: str, html_content: str) -> bool:
    if not _smtp_is_configured():
        print("⚠️ SMTP sozlanmagan — email yuborilmadi.")
        return False

    server = None
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        message.attach(MIMEText(html_content, "html", "utf-8"))
        server.sendmail(SENDER_EMAIL, [to_email], message.as_string())
        return True
    except (OSError, smtplib.SMTPException) as error:
        print(f"❌ Email yuborilmadi: {type(error).__name__}")
        return False
    finally:
        if server is not None:
            try:
                server.quit()
            except (OSError, smtplib.SMTPException):
                pass


def send_subscription_confirmation_email(to_email: str, confirmation_url: str) -> bool:
    """Foydalanuvchi roziligini tasdiqlash uchun bir martalik havola yuboradi."""
    safe_url = escape(confirmation_url, quote=True)
    html_content = f"""
    <!doctype html>
    <html lang="uz">
      <body style="font-family:Arial,sans-serif;background:#020617;color:#f8fafc;padding:20px">
        <div style="max-width:600px;margin:auto;padding:24px;border:1px solid #334155;border-radius:12px;background:#0f172a">
          <h1 style="color:#f59e0b">Biznes Darslari obunasi</h1>
          <p>Bu manzilga haftalik biznes darslari dayjestiga obuna so'rovi yuborildi.</p>
          <p>Obunani faollashtirish uchun quyidagi tugmani bosing. Agar so'rovni siz yubormagan bo'lsangiz, bu xatni e'tiborsiz qoldiring.</p>
          <p style="margin:28px 0"><a href="{safe_url}" style="background:#f59e0b;color:#111827;padding:12px 18px;border-radius:6px;text-decoration:none;font-weight:bold">Obunani tasdiqlash</a></p>
          <p style="font-size:12px;color:#94a3b8">Tasdiqlanmagan manzilga dayjest yuborilmaydi.</p>
        </div>
      </body>
    </html>
    """
    return _send_html_email(to_email, "Biznes Darslari — obunani tasdiqlang", html_content)


def _digest_html(articles: Sequence[dict], unsubscribe_url: str | None) -> str:
    items_html = ""
    for article in articles:
        link = f"{FRONTEND_ORIGIN.rstrip('/')}/maqola/{escape(str(article.get('slug', '')), quote=True)}"
        title = escape(str(article.get("title", "")))
        summary = escape(str(article.get("summary", "")))
        items_html += f"""
        <div style="margin-bottom:20px;padding:15px;border:1px solid #334155;border-radius:8px;background:#0f172a">
          <h3 style="margin:0 0 8px"><a href="{link}" style="color:#f59e0b;text-decoration:none">{title}</a></h3>
          <p style="margin:0 0 10px;color:#cbd5e1;font-size:14px">{summary}</p>
          <a href="{link}" style="display:inline-block;padding:6px 12px;background:#d97706;color:#fff;text-decoration:none;border-radius:4px;font-size:12px;font-weight:bold">To'liq o'qish →</a>
        </div>
        """

    unsubscribe_html = ""
    if unsubscribe_url:
        safe_unsubscribe_url = escape(unsubscribe_url, quote=True)
        unsubscribe_html = (
            f'<p><a href="{safe_unsubscribe_url}" style="color:#94a3b8">Obunani bekor qilish</a></p>'
        )

    return f"""
    <!doctype html>
    <html lang="uz">
      <body style="font-family:Arial,sans-serif;background:#020617;color:#f8fafc;padding:20px">
        <div style="max-width:600px;margin:auto;background:#090d16;padding:24px;border-radius:12px;border:1px solid #1e293b">
          <h1 style="color:#f59e0b;text-align:center;margin-bottom:4px">🎓 Biznes Darslari Dayjesti</h1>
          <p style="color:#94a3b8;text-align:center;margin-top:0">Siz uchun eng so'nggi amaliy darslar to'plami</p>
          {items_html}
          <div style="margin-top:24px;padding-top:16px;border-top:1px solid #334155;text-align:center;color:#64748b;font-size:12px">
            <p>Biznes Darslari ta'lim platformasi · <a href="{escape(FRONTEND_ORIGIN, quote=True)}" style="color:#94a3b8">Saytga o'tish</a></p>
            {unsubscribe_html}
          </div>
        </div>
      </body>
    </html>
    """


def send_email_digest(
    to_emails: Sequence[str],
    subject: str,
    articles: Sequence[dict],
    unsubscribe_urls: Mapping[str, str] | None = None,
) -> int:
    """Tasdiqlangan obunachilarga individual unsubscribe havolali dayjest yuboradi."""
    if not to_emails or not articles:
        return 0
    if not _smtp_is_configured():
        print("⚠️ SMTP sozlanmagan — dayjest yuborilmadi.")
        return 0

    sent_count = 0
    for email in to_emails:
        html_content = _digest_html(
            articles,
            unsubscribe_urls.get(email) if unsubscribe_urls else None,
        )
        if _send_html_email(email, subject, html_content):
            sent_count += 1
    return sent_count
