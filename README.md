<div align="center">

<img src="frontend/public/logo.png" width="96" alt="لوگوی نوین دیدگان" />

# کیوسک پذیرش جراحی — نوین دیدگان

سامانه‌ی پذیرش خودکار برای مرکز فوق‌تخصصی جراحی «نوین دیدگان»
<br/>
<sub>Self-service surgery-appointment kiosk · Vue 3 · FastAPI · PostgreSQL · Tauri 2</sub>

[![ci](https://github.com/OWNER/novin-kiosk/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/novin-kiosk/actions/workflows/ci.yml)

</div>

بیمار روی یک نمایشگر لمسی (یا گوشی) نوع عمل و پزشک را انتخاب می‌کند، نام و موبایل خود را وارد می‌کند و **کد پذیرش ۱۱ رقمی** و قبض چاپی را تحویل می‌گیرد. مدیر مرکز از پنل مدیریت نوبت‌ها، پزشکان، بیماران و گزارش‌ها را کنترل می‌کند.

> کد ملی از بیمار **دریافت نمی‌شود** (تصمیم طراحی).

## امکانات

- **جریان پذیرش:** دسته (چشم/زیبایی) ← نوع عمل چشم (تزریق/جراحی) ← پزشک ← نام و نام‌خانوادگی ← موبایل ← سابقه‌ی جراحی در مرکز ← بازبینی ← تأیید (کد را سرور صادر می‌کند).
- **سه چیدمان:** افقی (مانیتور بزرگ)، عمودی (مانیتور بالای ۲۰ اینچ) و موبایل. طراحی کاملاً بر پایه‌ی `rem` است و روی هر ابعاد مقیاس می‌گیرد.
- **ورودی لمسی:** صفحه‌کلید عددی و صفحه‌کلید فارسی مجازی (در موبایل ورودی بومی).
- **چاپ قبض:** تصویر ۵۷۶ پیکسلی ← ESC/POS raster از طریق Tauri (TCP:9100 یا دستگاه/اشتراک)؛ نیازی به فونت فارسی در چاپگر نیست.
- **حریم خصوصی:** بستن خودکار پرونده بعد از ۶۰ ثانیه بی‌حرکتی (+۱۵ ثانیه هشدار).
- **پنل مدیریت:** داشبورد، نوبت‌ها، پزشکان (عکس، نوع، تزریق)، بیماران، گزارش‌ها، ادمین‌ها، تنظیمات (تم).
- **تم روشن به‌صورت پیش‌فرض**؛ حالت تیره اختیاری است و فقط ادمین آن را فعال می‌کند.
- **قرارداد API ماشین‌خوان:** OpenAPI ← تایپ‌های TypeScript؛ ناهماهنگی فرانت و بک‌اند در CI شکست می‌خورد.
- **فونت‌ها:** میخک (فونت اصلی) و A Ghasem (لوگوتایپ) به‌صورت محلی همراه برنامه‌اند؛ بدون اینترنت کار می‌کند.

## ساختار مخزن

```
backend/     FastAPI + SQLAlchemy + Alembic          → API و منطق کسب‌وکار
frontend/    Vue 3 + Vite + TS + Pinia               → کیوسک و پنل مدیریت
src-tauri/   Tauri 2 (Rust)                          → پوسته‌ی تمام‌صفحه و چاپ قبض
docs/        مستندات + قرارداد API (openapi.json)
```

## شروع سریع (توسعه)

پیش‌نیاز: Docker، Python ۳٫۱۱+، Node ۲۲+.

```bash
cp .env.example .env                                  # SECRET_KEY را پر کنید
docker compose up -d db                               # PostgreSQL 16

cd backend
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
export DATABASE_URL=postgresql+psycopg://novin:change-me@localhost:5432/novin_kiosk
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed --demo                   # ادمین نمایشی (رمز SEED_ADMIN_PIN) + پزشک و نوبت نمونه
.venv/bin/uvicorn app.main:app --reload               # http://localhost:8000/docs

cd ../frontend && npm ci && npm run dev               # http://localhost:5173
```

- ورود به پنل مدیریت: ۵ لمس پشت‌سرهم روی لوگوی بالای کیوسک، یا `/#/admin/login`.
- در حالت توسعه، دکمه‌ی «نمای طراحی» برای دیدن هر سه چیدمان.

اجرای کامل سرور با Docker (دیتابیس + API): `docker compose up -d --build` — جزئیات در [راهنمای استقرار](docs/DEPLOYMENT.md).

## مستندات

| سند | موضوع |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | معماری، مدل داده، منطق کد پذیرش، احراز هویت، چاپ |
| [docs/API.md](docs/API.md) | قرارداد API (متن) · [`openapi.json`](docs/openapi.json) (ماشین‌خوان) |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | راه‌اندازی توسعه، تست، قرارداد API، طراحی/UI |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | استقرار سرور، نصب کیوسک (Tauri)، چاپگر، پشتیبان‌گیری |
| [docs/ADMIN-GUIDE.md](docs/ADMIN-GUIDE.md) | راهنمای کاربری پنل مدیریت و کیوسک |
| [CONTRIBUTING.md](CONTRIBUTING.md) | مشارکت و قواعد کد |
| [SECURITY.md](SECURITY.md) | امنیت و گزارش آسیب‌پذیری |
| [CHANGELOG.md](CHANGELOG.md) | تاریخچه‌ی تغییرات |

## تست

```bash
cd backend  && .venv/bin/pytest                       # ۱۷ تست؛ شامل تست قرارداد API
cd frontend && npm run typecheck && npm test && npm run build
cd src-tauri && cargo test                            # ماژول چاپگر
```

## مجوز

مجوزی هنوز انتخاب نشده است (همه‌ی حقوق محفوظ). پیش از عمومی‌کردن مخزن، فایل `LICENSE` را اضافه کنید.
