from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_admin
from ..models import Admin
from ..schemas import AdminOut, LoginIn, LoginOut
from ..security import create_token, limiter, verify_pin

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=LoginOut)
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    if limiter.locked(ip):
        raise HTTPException(429, "تلاش‌های ناموفق زیاد بود. چند دقیقه بعد دوباره امتحان کنید")
    for admin in db.scalars(select(Admin)):
        if verify_pin(data.pin, admin.pin_hash):
            limiter.ok(ip)
            return LoginOut(access_token=create_token(admin.id), admin=AdminOut.model_validate(admin))
    limiter.fail(ip)
    raise HTTPException(401, "رمز اشتباه است")


@router.get("/admin/me", response_model=AdminOut)
def me(admin: Admin = Depends(current_admin)):
    return admin
