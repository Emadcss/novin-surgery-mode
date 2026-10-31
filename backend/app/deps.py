import hmac

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import Admin
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def current_admin(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)
) -> Admin:
    admin_id = decode_token(cred.credentials) if cred else None
    admin = db.get(Admin, admin_id) if admin_id else None
    if not admin:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "ورود معتبر نیست", headers={"WWW-Authenticate": "Bearer"})
    return admin


def kiosk_guard(x_kiosk_key: str | None = Header(default=None)) -> None:
    if settings.kiosk_key and not hmac.compare_digest(x_kiosk_key or "", settings.kiosk_key):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "کلید کیوسک معتبر نیست")
