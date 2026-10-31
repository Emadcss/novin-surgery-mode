"""python -m app.seed [--demo]  — ساخت ادمین و پزشکان نمونه (و در صورت --demo نوبت‌های نمونه)."""
import random
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from .config import settings
from .db import SessionLocal
from .models import PROCEDURE_CATEGORY, Admin, Appointment, Category, Doctor, Procedure, Status
from .security import hash_pin
from .services import make_code, today_local

DOCTORS = [
    ("دکتر مهران صالحی", "فوق‌تخصص قرنیه و عیوب انکساری", Category.eye, True),
    ("دکتر لیلا نیک‌زاد", "جراح آب مروارید", Category.eye, False),
    ("دکتر امیر رضوانی", "متخصص شبکیه و ویتره", Category.eye, True),
    ("دکتر نگار فرهمند", "جراح و متخصص زیبایی", Category.cos, False),
    ("دکتر سعید کیانی", "جراح بینی و صورت", Category.cos, False),
]
PEOPLE = [("علی", "احمدی"), ("مریم", "کریمی"), ("رضا", "موسوی"), ("زهرا", "حسینی"), ("حسین", "رستمی"), ("فاطمه", "نظری"),
          ("محمد", "جعفری"), ("سارا", "قاسمی"), ("امیر", "باقری"), ("نرگس", "صادقی"), ("کاوه", "شریفی"), ("هانیه", "عباسی")]


def main(demo: bool) -> None:
    with SessionLocal() as db:
        if not db.scalar(select(func.count()).select_from(Admin)):
            db.add(Admin(name=settings.seed_admin_name, pin_hash=hash_pin(settings.seed_admin_pin)))
        if not db.scalar(select(func.count()).select_from(Doctor)):
            for i, (name, role, cat, inj) in enumerate(DOCTORS, 1):
                db.add(Doctor(no=i, name=name, role=role, category=cat, does_injection=inj))
        db.commit()
        if demo and not db.scalar(select(func.count()).select_from(Appointment)):
            rnd = random.Random(7)
            docs = list(db.scalars(select(Doctor).order_by(Doctor.no)))
            today = today_local()
            seqs: dict = {}
            for i in range(40):
                day = today - timedelta(days=rnd.choice([0, 0, 0, 1, 1, 2, 3, 4, 5, 6, 8, 10, 13]))
                doc = rnd.choice(docs)
                proc = Procedure.cos if doc.category == Category.cos else (
                    Procedure.inj_eye if doc.does_injection and rnd.random() < 0.35 else Procedure.surg_eye)
                seqs[day] = seqs.get(day, 0) + 1
                hist = rnd.random() < 0.3
                first, last = rnd.choice(PEOPLE)
                at = datetime(day.year, day.month, day.day, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=seqs[day] * 7)
                db.add(Appointment(
                    code=make_code(PROCEDURE_CATEGORY[proc], doc.no, day, hist, seqs[day]), seq=seqs[day], visit_date=day,
                    procedure=proc, category=PROCEDURE_CATEGORY[proc], doctor_id=doc.id, doctor_name=doc.name,
                    first_name=first, last_name=last, mobile=f"09120{rnd.randint(0, 9)}{rnd.randint(1000, 9999)}0"[:11],
                    has_history=hist, created_at=at,
                    status=Status.cancelled if rnd.random() < 0.08 else (Status.done if day < today else Status.booked),
                ))
            db.commit()
    print("seed ok", "(demo)" if demo else "")


if __name__ == "__main__":
    main("--demo" in sys.argv)
