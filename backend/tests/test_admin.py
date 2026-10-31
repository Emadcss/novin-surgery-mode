from datetime import timedelta

from app.services import today_local

from .conftest import book, png_bytes


def test_auth(client, seeded):
    assert client.get("/api/admin/doctors").status_code == 401
    assert client.post("/api/auth/login", json={"pin": "0000"}).status_code == 401
    ok = client.post("/api/auth/login", json={"pin": "۱۲۳۴"})
    assert ok.status_code == 200 and ok.json()["admin"]["name"] == "مدیر کل"
    h = {"Authorization": f"Bearer {ok.json()['access_token']}"}
    assert client.get("/api/admin/me", headers=h).json()["name"] == "مدیر کل"
    assert client.get("/api/admin/me", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_login_lockout(client, seeded):
    for _ in range(5):
        assert client.post("/api/auth/login", json={"pin": "9999"}).status_code == 401
    assert client.post("/api/auth/login", json={"pin": "1234"}).status_code == 429


def test_doctor_crud_and_photo(client, auth):
    r = client.post("/api/admin/doctors", headers=auth, json={"name": "دکتر پروانه شفیعی", "category": "eye"})
    assert r.status_code == 201
    d = r.json()
    assert d["does_injection"] is True and d["is_active"] is True and d["photo_url"] is None  # تزریق پیش‌فرض روشن
    cos = client.post("/api/admin/doctors", headers=auth, json={"name": "دکتر زیبایی", "category": "cos", "does_injection": True}).json()
    assert cos["does_injection"] is False and cos["no"] == d["no"] + 1
    # عکس
    up = client.post(f"/api/admin/doctors/{d['id']}/photo", headers=auth, files={"file": ("a.png", png_bytes(), "image/png")})
    assert up.status_code == 200 and up.json()["photo_url"].startswith("/media/doctors/")
    img = client.get(up.json()["photo_url"])
    assert img.status_code == 200 and img.headers["content-type"] == "image/jpeg"
    bad = client.post(f"/api/admin/doctors/{d['id']}/photo", headers=auth, files={"file": ("a.txt", b"nope", "text/plain")})
    assert bad.status_code == 422
    assert client.delete(f"/api/admin/doctors/{d['id']}/photo", headers=auth).json()["photo_url"] is None
    # ویرایش: خاموش‌کردن تزریق و تغییر گروه
    p = client.patch(f"/api/admin/doctors/{d['id']}", headers=auth, json={"does_injection": False}).json()
    assert p["does_injection"] is False
    assert client.patch(f"/api/admin/doctors/{d['id']}", headers=auth, json={"category": "cos"}).json()["category"] == "cos"
    # حذف نرم و عدم استفاده‌ی مجدد از شماره
    assert client.delete(f"/api/admin/doctors/{cos['id']}", headers=auth).status_code == 204
    ids = [x["id"] for x in client.get("/api/admin/doctors", headers=auth).json()]
    assert cos["id"] not in ids
    again = client.post("/api/admin/doctors", headers=auth, json={"name": "دکتر تازه", "category": "eye"}).json()
    assert again["no"] == cos["no"] + 1


def test_injection_toggle_hides_from_kiosk(client, auth):
    inj = lambda: [d["id"] for d in client.get("/api/kiosk/doctors", params={"procedure": "inj_eye"}).json()]  # noqa: E731
    assert 1 in inj()
    client.patch("/api/admin/doctors/1", headers=auth, json={"does_injection": False})
    assert 1 not in inj()
    assert any(d["id"] == 1 for d in client.get("/api/kiosk/doctors", params={"procedure": "surg_eye"}).json())
    client.patch("/api/admin/doctors/1", headers=auth, json={"is_active": False})
    assert all(d["id"] != 1 for d in client.get("/api/kiosk/doctors", params={"procedure": "surg_eye"}).json())


def test_appointments_admin(client, auth):
    a = book(client).json()
    b = book(client, procedure="cos", doctor_id=3, first_name="مریم", last_name="کریمی", mobile="09351112233", has_history=True).json()
    lst = client.get("/api/admin/appointments", headers=auth).json()
    assert lst["total"] == 2 and lst["items"][0]["id"] == b["id"]
    assert client.get("/api/admin/appointments", headers=auth, params={"q": "مریم"}).json()["total"] == 1
    assert client.get("/api/admin/appointments", headers=auth, params={"q": "۰۹۳۵۱"}).json()["total"] == 1
    assert client.get("/api/admin/appointments", headers=auth, params={"q": a["code"]}).json()["total"] == 1
    assert client.get("/api/admin/appointments", headers=auth, params={"category": "cos"}).json()["total"] == 1
    assert client.get("/api/admin/appointments", headers=auth, params={"doctor_id": 1}).json()["total"] == 1
    tomorrow = (today_local() + timedelta(days=1)).isoformat()
    assert client.get("/api/admin/appointments", headers=auth, params={"date_from": tomorrow}).json()["total"] == 0
    assert client.patch(f"/api/admin/appointments/{a['id']}", headers=auth, json={"status": "done"}).json()["status"] == "done"
    assert client.get("/api/admin/appointments", headers=auth, params={"status": "done"}).json()["total"] == 1
    assert client.delete(f"/api/admin/appointments/{b['id']}", headers=auth).status_code == 204
    assert client.get("/api/admin/appointments", headers=auth).json()["total"] == 1


def test_patients(client, auth):
    book(client)
    book(client, has_history=True)
    book(client, first_name="رضا", last_name="موسوی", mobile="09351112233")
    r = client.get("/api/admin/patients", headers=auth).json()
    assert r["total"] == 2
    by = {p["mobile"]: p for p in r["items"]}
    assert by["09123456789"]["appointments_count"] == 2 and len(by["09123456789"]["appointments"]) == 2
    assert client.get("/api/admin/patients", headers=auth, params={"q": "موسوی"}).json()["total"] == 1


def test_stats(client, auth):
    a = book(client).json()
    book(client, procedure="cos", doctor_id=3, has_history=True)
    book(client, procedure="inj_eye")
    client.patch(f"/api/admin/appointments/{a['id']}", headers=auth, json={"status": "cancelled"})
    d = client.get("/api/admin/stats/dashboard", headers=auth).json()
    assert d["today"] == {"total": 3, "booked": 2, "done": 0, "cancelled": 1}
    assert d["total_patients"] == 1 and d["history_count"] == 1 and d["total_doctors"] == 4 and d["active_doctors"] == 3
    assert len(d["last7"]) == 7 and d["last7"][-1]["count"] == 2
    today = today_local().isoformat()
    cal = client.get("/api/admin/stats/calendar", headers=auth, params={"date_from": today, "date_to": today}).json()
    assert cal == [{"date": today, "count": 3}]
    rep = client.get("/api/admin/stats/report", headers=auth, params={"days": 7}).json()
    assert rep["total"] == 3 and rep["cancelled"] == 1 and rep["with_history"] == 1
    assert {k["key"]: k["count"] for k in rep["by_procedure"]} == {"cos": 1, "inj_eye": 1}
    assert len(rep["per_day"]) == 14
    assert len(client.get("/api/admin/stats/report", headers=auth, params={"days": 30}).json()["per_day"]) == 30


def test_admins(client, auth):
    assert client.post("/api/admin/admins", headers=auth, json={"name": "منشی", "pin": "1234"}).status_code == 409
    assert client.post("/api/admin/admins", headers=auth, json={"name": "منشی", "pin": "12"}).status_code == 422
    new = client.post("/api/admin/admins", headers=auth, json={"name": "منشی", "pin": "۵۶۷۸"})
    assert new.status_code == 201
    assert client.post("/api/auth/login", json={"pin": "5678"}).status_code == 200
    me = client.get("/api/admin/me", headers=auth).json()
    assert client.delete(f"/api/admin/admins/{me['id']}", headers=auth).status_code == 400
    assert client.patch(f"/api/admin/admins/{new.json()['id']}", headers=auth, json={"pin": "1234"}).status_code == 409
    assert client.delete(f"/api/admin/admins/{new.json()['id']}", headers=auth).status_code == 204
