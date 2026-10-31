import io
import os
import tempfile

_media = tempfile.mkdtemp(prefix="kiosk-media-")
os.environ["MEDIA_DIR"] = _media
os.environ["BCRYPT_ROUNDS"] = "4"
os.environ["SECRET_KEY"] = "test-secret-key-test-secret-key-0123456789"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Admin, Category, Doctor  # noqa: E402
from app.security import hash_pin, limiter  # noqa: E402

TEST_URL = os.environ.get("TEST_DATABASE_URL", "sqlite://")


@pytest.fixture()
def db_engine():
    kw = {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}} if TEST_URL.startswith("sqlite") else {}
    engine = create_engine(TEST_URL, **kw)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def Session(db_engine):
    return sessionmaker(bind=db_engine, expire_on_commit=False)


@pytest.fixture()
def client(Session):
    def _db():
        with Session() as s:
            yield s

    app.dependency_overrides[get_db] = _db
    limiter.reset()
    settings.kiosk_key = ""
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seeded(Session):
    with Session() as s:
        s.add(Admin(name="مدیر کل", pin_hash=hash_pin("1234")))
        s.add_all([
            Doctor(no=1, name="دکتر مهران صالحی", role="قرنیه", category=Category.eye, does_injection=True),
            Doctor(no=2, name="دکتر لیلا نیک‌زاد", role="آب مروارید", category=Category.eye, does_injection=False),
            Doctor(no=3, name="دکتر نگار فرهمند", role="زیبایی", category=Category.cos, does_injection=False),
            Doctor(no=4, name="دکتر غیرفعال", role="", category=Category.eye, does_injection=True, is_active=False),
        ])
        s.commit()


@pytest.fixture()
def auth(client, seeded):
    r = client.post("/api/auth/login", json={"pin": "1234"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def png_bytes(size=(600, 400), color=(20, 120, 160)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    return buf.getvalue()


def book(client, **over):
    body = {"procedure": "surg_eye", "doctor_id": 1, "first_name": "علی", "last_name": "احمدی",
            "mobile": "09123456789", "has_history": False} | over
    return client.post("/api/kiosk/appointments", json=body)
