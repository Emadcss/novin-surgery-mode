# کیوسک پذیرش جراحی — نوین دیدگان

Vue 3 + FastAPI + PostgreSQL + Tauri

```
backend/    FastAPI + SQLAlchemy + Alembic (API و پنل مدیریت)
frontend/   Vue 3 + Vite + Pinia (کیوسک و پنل مدیریت؛ سه چیدمان: افقی، عمودی، موبایل)
src-tauri/  پوسته‌ی Tauri (تمام‌صفحه، چاپ قبض ESC/POS)
docs/API.md قرارداد API
```

## اجرا برای توسعه
```bash
cp .env.example .env
docker compose up -d db                    # PostgreSQL
cd backend && python -m venv .venv && .venv/bin/pip install -e ".[dev]"
export DATABASE_URL=postgresql+psycopg://novin:novin@localhost:5432/novin_kiosk
.venv/bin/alembic upgrade head && .venv/bin/python -m app.seed --demo   # ادمین نمایشی: رمز 1234
.venv/bin/uvicorn app.main:app --reload
cd ../frontend && npm i && npm run dev     # http://localhost:5173
```
- ورود به پنل مدیریت: ۵ لمس پشت‌سرهم روی لوگوی بالای کیوسک (یا آدرس `/#/admin/login`).
- دکمه‌ی «نمای طراحی» (فقط در حالت dev) برای مشاهده‌ی سه چیدمان.

## همه‌چیز با Docker (سرور)
`docker compose up -d --build` ← API روی پورت ۸۰۰۰ (migration و seed خودکار). قبل از استقرار `SECRET_KEY` و `KIOSK_KEY` و `SEED_ADMIN_PIN` را در `.env` عوض کنید.

## پوسته‌ی Tauri و چاپگر
1. `npm i` در ریشه، سپس `npm run icons` (ساخت آیکن‌ها از `src-tauri/app-icon.png`).
2. `src-tauri/kiosk.config.example.json` را کنار فایل اجرایی با نام `kiosk.config.json` بگذارید:
   - `api_base`: آدرس سرور FastAPI، `kiosk_key`: همان `KIOSK_KEY` سرور
   - `printer`: `tcp:IP:9100` یا مسیر دستگاه/اشتراک (`\\localhost\Receipt`، `\\.\USB001`، `/dev/usb/lp0`)
3. `npm run dev` (توسعه) یا `npm run build` (نصب‌کننده). پیش‌نیاز: Rust و وابستگی‌های Tauri برای سیستم‌عامل شما.

قبض به‌صورت تصویر (۵۷۶ پیکسل، ۸۰mm) رسم و به‌صورت ESC/POS raster چاپ می‌شود؛ پس نیازی به فونت فارسی در چاپگر نیست.
در مرورگر معمولی از `window.print()` استفاده می‌شود.

## تست
`cd backend && .venv/bin/pytest` (SQLite؛ برای Postgres مقدار `TEST_DATABASE_URL`) · `cd frontend && npm test` · ماژول چاپگر: `cargo test` روی `src-tauri/src/printer.rs`.

## نکات
- کد ملی دریافت نمی‌شود. کد پذیرش ۱۱ رقمی: تخصص(۱) + شماره پزشک(۲) + ماه‌روز شمسی(۴) + سابقه(۱) + نوبت روز(۳).
- پزشک با حذف نرم پاک می‌شود تا شماره‌ی او دوباره استفاده نشود.
