from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_admin, kiosk_guard
from ..models import Setting

Theme = Literal["light", "dark", "auto"]
DEFAULT_THEME: Theme = "light"  # در کلینیک نور محیط زیاد است؛ حالت تیره فقط با انتخاب ادمین فعال می‌شود


class SettingsOut(BaseModel):
    theme: Theme


class SettingsPatch(BaseModel):
    theme: Theme | None = None


def read_settings(db: Session) -> SettingsOut:
    row = db.get(Setting, "theme")
    return SettingsOut(theme=row.value if row and row.value in ("light", "dark", "auto") else DEFAULT_THEME)  # type: ignore[arg-type]


kiosk_router = APIRouter(prefix="/kiosk", tags=["kiosk"], dependencies=[Depends(kiosk_guard)])
admin_router = APIRouter(prefix="/admin/settings", tags=["settings"], dependencies=[Depends(current_admin)])


@kiosk_router.get("/settings", response_model=SettingsOut)
def kiosk_settings(db: Session = Depends(get_db)):
    return read_settings(db)


@admin_router.get("", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db)):
    return read_settings(db)


@admin_router.patch("", response_model=SettingsOut)
def patch_settings(data: SettingsPatch, db: Session = Depends(get_db)):
    if data.theme is not None:
        row = db.get(Setting, "theme")
        if row:
            row.value = data.theme
        else:
            db.add(Setting(key="theme", value=data.theme))
        db.commit()
    return read_settings(db)
