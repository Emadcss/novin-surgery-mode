import re
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_admin, kiosk_guard
from ..models import Setting

Theme = Literal["light", "dark", "auto"]
DEFAULT_THEME: Theme = "light"  # در کلینیک نور محیط زیاد است؛ حالت تیره فقط با انتخاب ادمین فعال می‌شود


TEXT_PREFIX = "text:"
TEXT_KEY_RE = re.compile(r"^[a-z0-9_.]{1,40}$")
TEXT_MAX_LEN = 300


class SettingsOut(BaseModel):
    theme: Theme
    # فقط متن‌هایی که ادمین تغییر داده است؛ برای بقیه، پیش‌فرض داخل برنامه‌ی کیوسک استفاده می‌شود
    texts: dict[str, str] = Field(default_factory=dict)


class SettingsPatch(BaseModel):
    theme: Theme | None = None
    # مقدار خالی یا null یعنی بازگشت به متن پیش‌فرض
    texts: dict[str, str | None] | None = None


def read_settings(db: Session) -> SettingsOut:
    row = db.get(Setting, "theme")
    texts = {
        r.key.removeprefix(TEXT_PREFIX): r.value
        for r in db.scalars(select(Setting).where(Setting.key.like(TEXT_PREFIX + "%")))
    }
    return SettingsOut(
        theme=row.value if row and row.value in ("light", "dark", "auto") else DEFAULT_THEME,  # type: ignore[arg-type]
        texts=texts,
    )


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
    for key, value in (data.texts or {}).items():
        if not TEXT_KEY_RE.match(key):
            raise HTTPException(422, "کلید متن نامعتبر است")
        value = (value or "").strip()
        if len(value) > TEXT_MAX_LEN:
            raise HTTPException(422, f"هر متن حداکثر {TEXT_MAX_LEN} نویسه می‌تواند باشد")
        row = db.get(Setting, TEXT_PREFIX + key)
        if not value:
            if row:
                db.delete(row)
        elif row:
            row.value = value
        else:
            db.add(Setting(key=TEXT_PREFIX + key, value=value))
    db.commit()
    return read_settings(db)
