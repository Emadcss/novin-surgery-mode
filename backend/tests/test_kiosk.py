import re

import jdatetime

from app.config import settings
from app.services import today_local

from .conftest import book


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_doctor_filters(client, seeded):
    names = lambda r: [d["name"] for d in r.json()]  # noqa: E731
    assert len(client.get("/api/kiosk/doctors").json()) == 3  # غیرفعال نمایش داده نمی‌شود
    eye = client.get("/api/kiosk/doctors", params={"category": "eye"})
    assert names(eye) == ["دکتر مهران صالحی", "دکتر لیلا نیک‌زاد"]
    inj = client.get("/api/kiosk/doctors", params={"procedure": "inj_eye"})
    assert names(inj) == ["دکتر مهران صالحی"]  # فقط دارنده‌ی تزریق
    surg = client.get("/api/kiosk/doctors", params={"procedure": "surg_eye"})
    assert len(surg.json()) == 2
    cos = client.get("/api/kiosk/doctors", params={"procedure": "cos"})
    assert names(cos) == ["دکتر نگار فرهمند"]


def test_book_and_code(client, seeded):
    r = book(client, has_history=True)
    assert r.status_code == 201, r.text
    ap = r.json()
    j = jdatetime.date.fromgregorian(date=today_local())
    assert re.fullmatch(r"101" + f"{j.month:02d}{j.day:02d}" + r"1001", ap["code"]), ap["code"]
    assert ap["seq"] == 1 and ap["status"] == "booked" and ap["category"] == "eye"
    assert book(client, procedure="cos", doctor_id=3).json()["seq"] == 2
    assert book(client, procedure="cos", doctor_id=3).json()["code"].startswith("203")


def test_input_validation(client, seeded):
    assert book(client, first_name="Ali").status_code == 422
    assert book(client, last_name="ا").status_code == 422
    assert book(client, mobile="08123456789").status_code == 422
    assert book(client, mobile="0912345").status_code == 422
    ok = book(client, mobile="۰۹۱۲۳۴۵۶۷۸۹", first_name="علي")
    assert ok.status_code == 201 and ok.json()["mobile"] == "09123456789" and ok.json()["first_name"] == "علی"


def test_doctor_availability_rules(client, seeded):
    assert book(client, procedure="inj_eye", doctor_id=2).status_code == 409  # بدون تزریق
    assert book(client, procedure="inj_eye", doctor_id=1).status_code == 201
    assert book(client, procedure="cos", doctor_id=1).status_code == 409  # گروه نادرست
    assert book(client, doctor_id=4).status_code == 409  # غیرفعال
    assert book(client, doctor_id=999).status_code == 409


def test_kiosk_key(client, seeded):
    settings.kiosk_key = "secret"
    try:
        assert client.get("/api/kiosk/doctors").status_code == 401
        assert client.get("/api/kiosk/doctors", headers={"X-Kiosk-Key": "secret"}).status_code == 200
    finally:
        settings.kiosk_key = ""
