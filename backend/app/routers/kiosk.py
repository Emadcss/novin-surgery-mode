from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import kiosk_guard
from ..models import PROCEDURE_CATEGORY, Category, Doctor, Procedure
from ..schemas import AppointmentIn, AppointmentOut, KioskDoctor
from ..services import create_appointment, doctor_available, doctor_counts, photo_url

router = APIRouter(prefix="/kiosk", tags=["kiosk"], dependencies=[Depends(kiosk_guard)])


@router.get("/doctors", response_model=list[KioskDoctor])
def kiosk_doctors(
    category: Category | None = Query(None), procedure: Procedure | None = Query(None), db: Session = Depends(get_db)
):
    if procedure and not category:
        category = PROCEDURE_CATEGORY[procedure]
    stmt = select(Doctor).where(Doctor.is_active.is_(True), Doctor.is_deleted.is_(False)).order_by(Doctor.no)
    if category:
        stmt = stmt.where(Doctor.category == category)
    doctors = [d for d in db.scalars(stmt) if not procedure or doctor_available(d, procedure)]
    _, today = doctor_counts(db, [d.id for d in doctors])
    return [
        KioskDoctor(
            id=d.id, name=d.name, role=d.role, category=d.category, does_injection=d.does_injection,
            photo_url=photo_url(d), today_count=today.get(d.id, 0),
        )
        for d in doctors
    ]


@router.post("/appointments", response_model=AppointmentOut, status_code=201)
def kiosk_create(data: AppointmentIn, db: Session = Depends(get_db)):
    return create_appointment(db, data)
