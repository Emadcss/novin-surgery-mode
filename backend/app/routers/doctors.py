from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_admin
from ..models import Category, Doctor
from ..schemas import DoctorIn, DoctorOut, DoctorPatch
from ..services import doctor_out, next_doctor_no, remove_photo, save_photo

router = APIRouter(prefix="/admin/doctors", tags=["doctors"], dependencies=[Depends(current_admin)])


def _get(db: Session, doctor_id: int) -> Doctor:
    d = db.get(Doctor, doctor_id)
    if not d or d.is_deleted:
        raise HTTPException(404, "پزشک پیدا نشد")
    return d


@router.get("", response_model=list[DoctorOut])
def list_doctors(db: Session = Depends(get_db)):
    return doctor_out(db, list(db.scalars(select(Doctor).where(Doctor.is_deleted.is_(False)).order_by(Doctor.no))))


@router.post("", response_model=DoctorOut, status_code=201)
def create_doctor(data: DoctorIn, db: Session = Depends(get_db)):
    d = Doctor(
        no=next_doctor_no(db), name=data.name.strip(), role=data.role.strip(), category=data.category,
        does_injection=data.does_injection and data.category == Category.eye, is_active=data.is_active,
    )
    db.add(d)
    db.commit()
    return doctor_out(db, [d])[0]


@router.patch("/{doctor_id}", response_model=DoctorOut)
def patch_doctor(doctor_id: int, data: DoctorPatch, db: Session = Depends(get_db)):
    d = _get(db, doctor_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(d, k, v.strip() if isinstance(v, str) else v)
    if d.category == Category.cos:
        d.does_injection = False
    db.commit()
    return doctor_out(db, [d])[0]


@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    d = _get(db, doctor_id)
    remove_photo(d)
    d.is_deleted, d.is_active = True, False
    db.commit()


@router.post("/{doctor_id}/photo", response_model=DoctorOut)
def upload_photo(doctor_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    d = _get(db, doctor_id)
    save_photo(d, file)
    db.commit()
    return doctor_out(db, [d])[0]


@router.delete("/{doctor_id}/photo", response_model=DoctorOut)
def delete_photo(doctor_id: int, db: Session = Depends(get_db)):
    d = _get(db, doctor_id)
    remove_photo(d)
    db.commit()
    return doctor_out(db, [d])[0]
