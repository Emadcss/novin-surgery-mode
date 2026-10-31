import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import admins, appointments, auth, doctors, kiosk, patients, app_settings, stats


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.secret_key == "change-me":
        logging.getLogger("uvicorn.error").warning("SECRET_KEY مقدار پیش‌فرض دارد؛ برای محیط واقعی حتماً تغییرش دهید")
    (settings.media_dir / "doctors").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Novin Kiosk API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")
for r in (kiosk.router, auth.router, doctors.router, appointments.router, patients.router, stats.router, admins.router, app_settings.kiosk_router, app_settings.admin_router):
    api.include_router(r)


@api.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


app.include_router(api)
settings.media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
