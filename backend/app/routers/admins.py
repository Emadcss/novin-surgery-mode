from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_admin
from ..models import Admin
from ..schemas import AdminCreate, AdminOut, AdminPatch
from ..security import hash_pin, verify_pin

router = APIRouter(prefix="/admin/admins", tags=["admins"], dependencies=[Depends(current_admin)])


def _pin_taken(db: Session, pin: str, except_id: int | None = None) -> bool:
    return any(verify_pin(pin, a.pin_hash) for a in db.scalars(select(Admin)) if a.id != except_id)


@router.get("", response_model=list[AdminOut])
def list_admins(db: Session = Depends(get_db)):
    return list(db.scalars(select(Admin).order_by(Admin.id)))


@router.post("", response_model=AdminOut, status_code=201)
def create_admin(data: AdminCreate, db: Session = Depends(get_db)):
    if _pin_taken(db, data.pin):
        raise HTTPException(409, "این رمز برای ادمین دیگری استفاده شده است")
    admin = Admin(name=data.name.strip(), pin_hash=hash_pin(data.pin))
    db.add(admin)
    db.commit()
    return admin


@router.patch("/{admin_id}", response_model=AdminOut)
def patch_admin(admin_id: int, data: AdminPatch, db: Session = Depends(get_db)):
    admin = db.get(Admin, admin_id)
    if not admin:
        raise HTTPException(404, "ادمین پیدا نشد")
    if data.pin is not None:
        if _pin_taken(db, data.pin, admin.id):
            raise HTTPException(409, "این رمز برای ادمین دیگری استفاده شده است")
        admin.pin_hash = hash_pin(data.pin)
    if data.name is not None:
        admin.name = data.name.strip()
    db.commit()
    return admin


@router.delete("/{admin_id}", status_code=204)
def delete_admin(admin_id: int, me: Admin = Depends(current_admin), db: Session = Depends(get_db)):
    admin = db.get(Admin, admin_id)
    if not admin:
        raise HTTPException(404, "ادمین پیدا نشد")
    if admin.id == me.id:
        raise HTTPException(400, "نمی‌توانید خودتان را حذف کنید")
    if (db.scalar(select(func.count()).select_from(Admin)) or 0) < 2:
        raise HTTPException(400, "حداقل یک ادمین باید باقی بماند")
    db.delete(admin)
    db.commit()
