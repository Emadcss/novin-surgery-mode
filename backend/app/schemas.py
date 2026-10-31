import re
from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import Category, Procedure, Status

_FA_DIGITS = {ord(c): str(i) for i, c in enumerate("۰۱۲۳۴۵۶۷۸۹")} | {ord(c): str(i) for i, c in enumerate("٠١٢٣٤٥٦٧٨٩")}
_FA_NAME = re.compile(r"^[ء-ھۀ-ی‌ ]{2,24}$")


def to_en_digits(s: str) -> str:
    return s.translate(_FA_DIGITS)


def clean_name(v: str) -> str:
    v = v.replace("ي", "ی").replace("ك", "ک").strip()
    v = re.sub(r"\s+", " ", v)
    if not _FA_NAME.match(v) or len(v.replace("‌", "").replace(" ", "")) < 2:
        raise ValueError("نام باید فارسی و بین ۲ تا ۲۴ حرف باشد")
    return v


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- kiosk ----------
class KioskDoctor(BaseModel):
    id: int
    name: str
    role: str
    category: Category
    does_injection: bool
    photo_url: str | None
    today_count: int


class AppointmentIn(BaseModel):
    procedure: Procedure
    doctor_id: int
    first_name: str
    last_name: str
    mobile: str
    has_history: bool

    _fn = field_validator("first_name", "last_name")(lambda cls, v: clean_name(v))

    @field_validator("mobile")
    @classmethod
    def _mobile(cls, v: str) -> str:
        v = to_en_digits(v).replace(" ", "")
        if not re.fullmatch(r"09\d{9}", v):
            raise ValueError("شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد")
        return v


class AppointmentOut(ORM):
    id: int
    code: str
    seq: int
    procedure: Procedure
    category: Category
    doctor_id: int | None
    doctor_name: str
    first_name: str
    last_name: str
    mobile: str
    has_history: bool
    status: Status
    visit_date: date
    created_at: datetime


class AppointmentPatch(BaseModel):
    status: Status


class AppointmentPage(BaseModel):
    items: list[AppointmentOut]
    total: int


# ---------- auth / admins ----------
class LoginIn(BaseModel):
    pin: str

    @field_validator("pin")
    @classmethod
    def _pin(cls, v: str) -> str:
        return to_en_digits(v).strip()


class AdminOut(ORM):
    id: int
    name: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminOut


def _check_pin(v: str) -> str:
    v = to_en_digits(v).strip()
    if not re.fullmatch(r"\d{4}", v):
        raise ValueError("رمز باید چهار رقم باشد")
    return v


class AdminCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=60)]
    pin: str
    _p = field_validator("pin")(lambda cls, v: _check_pin(v))


class AdminPatch(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=60)] | None = None
    pin: str | None = None

    @field_validator("pin")
    @classmethod
    def _p(cls, v: str | None) -> str | None:
        return _check_pin(v) if v is not None else v


# ---------- doctors ----------
class DoctorOut(BaseModel):
    id: int
    no: int
    name: str
    role: str
    category: Category
    does_injection: bool
    is_active: bool
    photo_url: str | None
    today_count: int
    total_count: int


class DoctorIn(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=80)]
    role: Annotated[str, Field(max_length=120)] = ""
    category: Category
    does_injection: bool = True
    is_active: bool = True


class DoctorPatch(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=80)] | None = None
    role: Annotated[str, Field(max_length=120)] | None = None
    category: Category | None = None
    does_injection: bool | None = None
    is_active: bool | None = None


# ---------- patients / stats ----------
class PatientOut(BaseModel):
    mobile: str
    first_name: str
    last_name: str
    appointments_count: int
    last_visit_date: date
    appointments: list[AppointmentOut]


class PatientPage(BaseModel):
    items: list[PatientOut]
    total: int


class DayCount(BaseModel):
    date: date
    count: int


class KeyCount(BaseModel):
    key: str
    count: int


class TodayStats(BaseModel):
    total: int
    booked: int
    done: int
    cancelled: int


class DashboardOut(BaseModel):
    today: TodayStats
    total_appointments: int
    total_patients: int
    history_count: int
    active_doctors: int
    total_doctors: int
    last7: list[DayCount]


class ReportOut(BaseModel):
    total: int
    done: int
    cancelled: int
    with_history: int
    per_day: list[DayCount]
    by_category: list[KeyCount]
    by_procedure: list[KeyCount]
    by_doctor: list[KeyCount]
