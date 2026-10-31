import io
import uuid
from datetime import date, datetime
from zoneinfo import ZoneInfo

import jdatetime
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .models import PROCEDURE_CATEGORY, Appointment, Category, Doctor, Procedure, Status
from .schemas import AppointmentIn, DoctorOut

Image.MAX_IMAGE_PIXELS = 40_000_000
MAX_UPLOAD = 8 * 1024 * 1024
CATEGORY_DIGIT = {Category.eye: "1", Category.cos: "2"}


def now_local() -> datetime:
    return datetime.now(ZoneInfo(settings.timezone))


def today_local() -> date:
    return now_local().date()


def make_code(category: Category, doctor_no: int, visit: date, has_history: bool, seq: int) -> str:
    j = jdatetime.date.fromgregorian(date=visit)
    return f"{CATEGORY_DIGIT[category]}{doctor_no:02d}{j.month:02d}{j.day:02d}{int(has_history)}{seq:03d}"


# ---------- doctors ----------
def photo_url(d: Doctor) -> str | None:
    return f"/media/{d.photo_path}" if d.photo_path else None


def doctor_counts(db: Session, ids: list[int]) -> tuple[dict[int, int], dict[int, int]]:
    if not ids:
        return {}, {}
    total = dict(
        db.execute(
            select(Appointment.doctor_id, func.count()).where(Appointment.doctor_id.in_(ids)).group_by(Appointment.doctor_id)
        ).all()
    )
    today = dict(
        db.execute(
            select(Appointment.doctor_id, func.count())
            .where(
                Appointment.doctor_id.in_(ids),
                Appointment.visit_date == today_local(),
                Appointment.status != Status.cancelled,
            )
            .group_by(Appointment.doctor_id)
        ).all()
    )
    return total, today


def doctor_out(db: Session, doctors: list[Doctor]) -> list[DoctorOut]:
    total, today = doctor_counts(db, [d.id for d in doctors])
    return [
        DoctorOut(
            id=d.id, no=d.no, name=d.name, role=d.role, category=d.category,
            does_injection=d.does_injection, is_active=d.is_active, photo_url=photo_url(d),
            today_count=today.get(d.id, 0), total_count=total.get(d.id, 0),
        )
        for d in doctors
    ]


def next_doctor_no(db: Session) -> int:
    return (db.scalar(select(func.coalesce(func.max(Doctor.no), 0))) or 0) + 1


def doctor_available(d: Doctor, procedure: Procedure) -> bool:
    return (
        d.is_active
        and not d.is_deleted
        and d.category == PROCEDURE_CATEGORY[procedure]
        and (procedure != Procedure.inj_eye or d.does_injection)
    )


# ---------- photos ----------
def save_photo(doctor: Doctor, file: UploadFile) -> None:
    raw = file.file.read(MAX_UPLOAD + 1)
    if len(raw) > MAX_UPLOAD:
        raise HTTPException(413, "حجم تصویر بیش از ۸ مگابایت است")
    try:
        im = Image.open(io.BytesIO(raw))
        im.verify()
        im = Image.open(io.BytesIO(raw))
        im = ImageOps.exif_transpose(im).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(422, "فایل انتخاب‌شده تصویر معتبر نیست")
    im = ImageOps.fit(im, (320, 320), method=Image.LANCZOS)
    folder = settings.media_dir / "doctors"
    folder.mkdir(parents=True, exist_ok=True)
    name = f"doctors/{doctor.id}-{uuid.uuid4().hex[:8]}.jpg"
    im.save(settings.media_dir / name, "JPEG", quality=85, optimize=True)
    remove_photo(doctor)
    doctor.photo_path = name


def remove_photo(doctor: Doctor) -> None:
    if doctor.photo_path:
        (settings.media_dir / doctor.photo_path).unlink(missing_ok=True)
        doctor.photo_path = None


# ---------- appointments ----------
def create_appointment(db: Session, data: AppointmentIn) -> Appointment:
    doctor = db.get(Doctor, data.doctor_id)
    if not doctor or not doctor_available(doctor, data.procedure):
        raise HTTPException(409, "این پزشک در حال حاضر برای این نوع جراحی در دسترس نیست")
    visit = today_local()
    category = PROCEDURE_CATEGORY[data.procedure]
    for _ in range(6):
        seq = (db.scalar(select(func.coalesce(func.max(Appointment.seq), 0)).where(Appointment.visit_date == visit)) or 0) + 1
        ap = Appointment(
            code=make_code(category, doctor.no, visit, data.has_history, seq),
            seq=seq, visit_date=visit, procedure=data.procedure, category=category,
            doctor_id=doctor.id, doctor_name=doctor.name, first_name=data.first_name,
            last_name=data.last_name, mobile=data.mobile, has_history=data.has_history,
        )
        db.add(ap)
        try:
            db.commit()
            db.refresh(ap)
            return ap
        except IntegrityError:  # دو کیوسک هم‌زمان شماره‌ی نوبت یکسان گرفتند
            db.rollback()
    raise HTTPException(503, "ثبت نوبت انجام نشد. دوباره تلاش کنید")
