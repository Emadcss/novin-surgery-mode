import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Category(str, enum.Enum):
    eye = "eye"
    cos = "cos"


class Procedure(str, enum.Enum):
    inj_eye = "inj_eye"
    surg_eye = "surg_eye"
    cos = "cos"


class Status(str, enum.Enum):
    booked = "booked"
    done = "done"
    cancelled = "cancelled"


PROCEDURE_CATEGORY = {
    Procedure.inj_eye: Category.eye,
    Procedure.surg_eye: Category.eye,
    Procedure.cos: Category.cos,
}


def _enum(cls, name):
    return Enum(cls, name=name, native_enum=False, length=16, validate_strings=True)


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    pin_hash: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True)
    # شماره‌ی پزشک در کد پذیرش؛ هرگز دوباره استفاده نمی‌شود (حذف نرم)
    no: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(120), default="")
    category: Mapped[Category] = mapped_column(_enum(Category, "category"))
    does_injection: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_path: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (UniqueConstraint("visit_date", "seq", name="uq_appointment_day_seq"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(11), index=True)
    seq: Mapped[int] = mapped_column(Integer)
    visit_date: Mapped[date] = mapped_column(Date, index=True)
    procedure: Mapped[Procedure] = mapped_column(_enum(Procedure, "procedure"))
    category: Mapped[Category] = mapped_column(_enum(Category, "category_ap"))
    doctor_id: Mapped[int | None] = mapped_column(ForeignKey("doctors.id"), nullable=True)
    doctor_name: Mapped[str] = mapped_column(String(80))
    first_name: Mapped[str] = mapped_column(String(40))
    last_name: Mapped[str] = mapped_column(String(40))
    mobile: Mapped[str] = mapped_column(String(11), index=True)
    has_history: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[Status] = mapped_column(_enum(Status, "status"), default=Status.booked)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    doctor: Mapped[Doctor | None] = relationship(back_populates="appointments")
