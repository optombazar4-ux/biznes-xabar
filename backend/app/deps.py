import secrets
from fastapi import Header, HTTPException
from .config import ADMIN_TOKEN, admin_is_configured
from .security import verify_access_token


def require_admin(
    authorization: str = Header(default=""),
    x_admin_token: str = Header(default=""),
):
    """Admin huquqini tekshiradi: Authorization Bearer JWT token yoki X-Admin-Token header."""
    if not admin_is_configured():
        raise HTTPException(
            status_code=503,
            detail="Admin panel xavfsiz token sozlanguncha o'chirilgan",
        )

    # 1. Bearer JWT token tekshiruvi
    if authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        payload = verify_access_token(token)
        if payload and payload.get("role") == "admin":
            return payload

    # 2. Eskicha X-Admin-Token mosligi
    if x_admin_token:
        if secrets.compare_digest(x_admin_token, ADMIN_TOKEN):
            return {"role": "admin", "sub": "legacy-header"}

    raise HTTPException(status_code=401, detail="Ruxsat berilmadi: Noto'g'ri token yoki login talab qilinadi")
