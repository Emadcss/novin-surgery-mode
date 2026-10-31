from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_admin
from ..models import Appointment, Doctor, Status
from ..schemas import DashboardOut, DayCount, KeyCount, ReportOut, TodayStats
from ..services import today_local

router = APIRouter(prefix="/admin/stats", tags=["stats"], dependencies=[Depends(current_admin)])


def _per_day(db: Session, start: date, end: date, *extra) -> list[DayCount]:
    rows = dict(
        db.execute(
            select(Appointment.visit_date, func.count())
            .where(Appointment.visit_date.between(start, end), Appointment.status != Status.cancelled, *extra)
            .group_by(Appointment.visit_date)
        ).all()
    )
    return [DayCount(date=start + timedelta(days=i), count=rows.get(start + timedelta(days=i), 0)) for i in range((end - start).days + 1)]


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    today = today_local()
    by_status = dict(
        db.execute(select(Appointment.status, func.count()).where(Appointment.visit_date == today).group_by(Appointment.status)).all()
    )
    docs = db.execute(
        select(func.count(), func.coalesce(func.sum(case((Doctor.is_active.is_(True), 1), else_=0)), 0)).where(Doctor.is_deleted.is_(False))
    ).one()
    return DashboardOut(
        today=TodayStats(
            total=sum(by_status.values()), booked=by_status.get(Status.booked, 0),
            done=by_status.get(Status.done, 0), cancelled=by_status.get(Status.cancelled, 0),
        ),
        total_appointments=db.scalar(select(func.count()).select_from(Appointment)) or 0,
        total_patients=db.scalar(select(func.count(func.distinct(Appointment.mobile)))) or 0,
        history_count=db.scalar(select(func.count()).select_from(Appointment).where(Appointment.has_history.is_(True))) or 0,
        active_doctors=int(docs[1]),
        total_doctors=int(docs[0]),
        last7=_per_day(db, today - timedelta(days=6), today),
    )


@router.get("/calendar", response_model=list[DayCount])
def calendar(date_from: date, date_to: date, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Appointment.visit_date, func.count())
        .where(Appointment.visit_date.between(date_from, date_to))
        .group_by(Appointment.visit_date)
        .order_by(Appointment.visit_date)
    ).all()
    return [DayCount(date=d, count=c) for d, c in rows]


@router.get("/report", response_model=ReportOut)
def report(days: int = Query(7, ge=0, le=3650), db: Session = Depends(get_db)):
    today = today_local()
    conds = [] if days == 0 else [Appointment.visit_date > today - timedelta(days=days)]
    live = [*conds, Appointment.status != Status.cancelled]

    def count_by(col):
        rows = db.execute(select(col, func.count()).where(*live).group_by(col).order_by(func.count().desc())).all()
        return [KeyCount(key=getattr(k, "value", str(k)), count=c) for k, c in rows]

    by_status = dict(db.execute(select(Appointment.status, func.count()).where(*conds).group_by(Appointment.status)).all())
    span = 30 if days == 30 else 14
    return ReportOut(
        total=sum(by_status.values()),
        done=by_status.get(Status.done, 0),
        cancelled=by_status.get(Status.cancelled, 0),
        with_history=db.scalar(select(func.count()).select_from(Appointment).where(*conds, Appointment.has_history.is_(True))) or 0,
        per_day=_per_day(db, today - timedelta(days=span - 1), today),
        by_category=count_by(Appointment.category),
        by_procedure=count_by(Appointment.procedure),
        by_doctor=count_by(Appointment.doctor_name),
    )
