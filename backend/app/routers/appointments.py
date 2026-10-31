from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_admin
from ..models import Appointment, Category, Status
from ..schemas import AppointmentOut, AppointmentPage, AppointmentPatch, to_en_digits

router = APIRouter(prefix="/admin/appointments", tags=["appointments"], dependencies=[Depends(current_admin)])


@router.get("", response_model=AppointmentPage)
def list_appointments(
    q: str | None = None,
    category: Category | None = None,
    status: Status | None = None,
    doctor_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    conds = []
    if category:
        conds.append(Appointment.category == category)
    if status:
        conds.append(Appointment.status == status)
    if doctor_id:
        conds.append(Appointment.doctor_id == doctor_id)
    if date_from:
        conds.append(Appointment.visit_date >= date_from)
    if date_to:
        conds.append(Appointment.visit_date <= date_to)
    if q and q.strip():
        term = q.strip()
        digits = to_en_digits(term)
        full = Appointment.first_name + " " + Appointment.last_name
        conds.append(or_(full.ilike(f"%{term}%"), Appointment.mobile.contains(digits), Appointment.code.contains(digits)))
    total = db.scalar(select(func.count()).select_from(Appointment).where(*conds)) or 0
    items = db.scalars(
        select(Appointment).where(*conds).order_by(Appointment.created_at.desc(), Appointment.id.desc()).limit(limit).offset(offset)
    ).all()
    return AppointmentPage(items=items, total=total)


@router.patch("/{ap_id}", response_model=AppointmentOut)
def patch_appointment(ap_id: int, data: AppointmentPatch, db: Session = Depends(get_db)):
    ap = db.get(Appointment, ap_id)
    if not ap:
        raise HTTPException(404, "نوبت پیدا نشد")
    ap.status = data.status
    db.commit()
    return ap


@router.delete("/{ap_id}", status_code=204)
def delete_appointment(ap_id: int, db: Session = Depends(get_db)):
    ap = db.get(Appointment, ap_id)
    if not ap:
        raise HTTPException(404, "نوبت پیدا نشد")
    db.delete(ap)
    db.commit()
