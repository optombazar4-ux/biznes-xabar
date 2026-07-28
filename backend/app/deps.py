import secrets

from fastapi import Header, HTTPException

from .config import ADMIN_TOKEN, admin_is_configured


def require_admin(x_admin_token: str = Header(default="")):
    if not admin_is_configured():
        raise HTTPException(status_code=503, detail="Admin panel xavfsiz token sozlanguncha o'chirilgan")
    if not secrets.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Admin token noto'g'ri")
