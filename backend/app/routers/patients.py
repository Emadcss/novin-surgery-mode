from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_admin
from ..models import Appointment
from ..schemas import PatientOut, PatientPage, to_en_digits

router = APIRouter(prefix="/admin/patients", tags=["patients"], dependencies=[Depends(current_admin)])


@router.get("", response_model=PatientPage)
def list_patients(
    q: str | None = None, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db)
):
    conds = []
    if q and q.strip():
        term = q.strip()
        full = Appointment.first_name + " " + Appointment.last_name
        conds.append(full.ilike(f"%{term}%") | Appointment.mobile.contains(to_en_digits(term)))
    grouped = (
        select(Appointment.mobile, func.max(Appointment.created_at).label("last"))
        .where(*conds)
        .group_by(Appointment.mobile)
    )
    total = db.scalar(select(func.count()).select_from(grouped.subquery())) or 0
    page = db.execute(grouped.order_by(func.max(Appointment.created_at).desc()).limit(limit).offset(offset)).all()
    mobiles = [r.mobile for r in page]
    rows = db.scalars(
        select(Appointment).where(Appointment.mobile.in_(mobiles)).order_by(Appointment.created_at.desc(), Appointment.id.desc())
    ).all()
    by: dict[str, list[Appointment]] = {m: [] for m in mobiles}
    for ap in rows:
        by[ap.mobile].append(ap)
    items = [
        PatientOut(
            mobile=m, first_name=by[m][0].first_name, last_name=by[m][0].last_name,
            appointments_count=len(by[m]), last_visit_date=by[m][0].visit_date, appointments=by[m],
        )
        for m in mobiles
    ]
    return PatientPage(items=items, total=total)
