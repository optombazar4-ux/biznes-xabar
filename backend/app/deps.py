from fastapi import Header, HTTPException
from .config import admin_is_configured
from .security import verify_access_token


def require_admin(authorization: str = Header(default="")):
    """Admin huquqini faqat qisqa muddatli Bearer JWT bilan tekshiradi."""
    if not admin_is_configured():
        raise HTTPException(
            status_code=503,
            detail="Admin panel xavfsiz token sozlanguncha o'chirilgan",
        )

    if authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        payload = verify_access_token(token)
        if payload and payload.get("role") == "admin":
            return payload

    raise HTTPException(status_code=401, detail="Ruxsat berilmadi: Noto'g'ri token yoki login talab qilinadi")
