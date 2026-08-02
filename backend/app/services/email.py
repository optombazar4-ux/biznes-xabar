"""Email Dayjest va Bildirishnomalar Servisi.

SMTP yoki konsol (mock) orqali obunachilarga HTML formatda haftalik/kunlik
dayjest va yangiliklar xatlarini yuboradi.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from ..config import FRONTEND_ORIGIN

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@biznesxabar.uz")


def send_email_digest(to_emails: List[str], subject: str, articles: List[dict]) -> int:
    """Obunachilarga HTML dayjest yuboradi va muvaffaqiyatli yuborilganlar sonini qaytaradi."""
    if not to_emails or not articles:
        return 0

    # HTML Email Shablonini yaratish
    items_html = ""
    for art in articles:
        link = f"{FRONTEND_ORIGIN}/maqola/{art.get('slug')}"
        items_html += f"""
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #334155; border-radius: 8px; background-color: #0f172a;">
            <h3 style="margin: 0 0 8px 0;"><a href="{link}" style="color: #f59e0b; text-decoration: none;">{art.get('title')}</a></h3>
            <p style="margin: 0 0 10px 0; color: #cbd5e1; font-size: 14px;">{art.get('summary')}</p>
            <a href="{link}" style="display: inline-block; padding: 6px 12px; background-color: #d97706; color: #ffffff; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: bold;">To'liq o'qish →</a>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #020617; color: #f8fafc; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #090d16; padding: 24px; border-radius: 12px; border: 1px solid #1e293b;">
            <h1 style="color: #f59e0b; text-align: center; margin-bottom: 4px;">🎓 Biznes Darslari Dayjesti</h1>
            <p style="color: #94a3b8; text-align: center; margin-top: 0;">Siz uchun eng so'nggi amaliy darslar toplami</p>
            {items_html}
            <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #334155; text-align: center; color: #64748b; font-size: 12px;">
                <p>Biznes Darslari ta'lim platformasi · <a href="{FRONTEND_ORIGIN}" style="color: #94a3b8;">Saytga o'tish</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Agar SMTP sozlanmagan bo'lsa, konsolda simulyatsiya qilamiz
    if not SMTP_HOST or not SMTP_USER:
        print(f"📧 [MOCK EMAIL] '{subject}' sarlavhali dayjest {len(to_emails)} ta obunachiga yuborildi (SMTP sozlanmagan).")
        return len(to_emails)

    sent_count = 0
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)

        for email in to_emails:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SENDER_EMAIL
            msg["To"] = email
            msg.attach(MIMEText(html_content, "html"))
            
            server.sendmail(SENDER_EMAIL, email, msg.as_string())
            sent_count += 1

        server.quit()
    except Exception as err:
        print(f"❌ Email yuborishda xatolik: {err}")

    return sent_count
