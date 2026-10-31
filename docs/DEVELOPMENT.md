# راهنمای توسعه

## پیش‌نیازها

| ابزار | نسخه |
|---|---|
| Python | ۳٫۱۱ به بالا (Docker image از ۳٫۱۲) |
| Node.js | ۲۲ |
| Docker | برای PostgreSQL 16 |
| Rust + پیش‌نیازهای Tauri | فقط برای ساخت پوسته‌ی دسکتاپ ([راهنمای Tauri](https://tauri.app/start/prerequisites/)) |

## راه‌اندازی

```bash
cp .env.example .env            # POSTGRES_PASSWORD و SECRET_KEY را پر کنید (openssl rand -hex 32)
docker compose up -d db
```

### بک‌اند
```bash
cd backend
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
cp .env.example .env            # DATABASE_URL را با رمز دیتابیس هماهنگ کنید
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed --demo
.venv/bin/uvicorn app.main:app --reload
```
مستندات تعاملی: <http://localhost:8000/docs>

### فرانت‌اند
```bash
cd frontend
npm ci
npm run dev                     # http://localhost:5173
```
در حالت توسعه، `/api` و `/media` توسط Vite به `http://localhost:8000` پروکسی می‌شوند (تغییر با `VITE_DEV_API`). آدرس API در بیلد تولید از `VITE_API_BASE` (زمان بیلد) یا در Tauri از `kiosk.config.json` خوانده می‌شود؛ اگر هیچ‌کدام نباشد، هم‌مبدأ (همان دامنه‌ی صفحه) است. کلید کیوسک: `VITE_KIOSK_KEY` یا `kiosk_key` در کانفیگ Tauri.

### پوسته‌ی Tauri
```bash
npm i                           # در ریشه
npm run icons                   # ساخت آیکن‌ها از src-tauri/app-icon.png
cp src-tauri/kiosk.config.example.json src-tauri/kiosk.config.json   # و مقادیر را ویرایش کنید
npm run dev
```

## دستورات پرکاربرد

| کار | دستور |
|---|---|
| تست بک‌اند | `cd backend && .venv/bin/pytest` |
| تست بک‌اند روی Postgres | `TEST_DATABASE_URL=postgresql+psycopg://… pytest` |
| تایپ‌چک فرانت | `cd frontend && npm run typecheck` |
| تست واحد فرانت | `cd frontend && npm test` |
| بیلد فرانت | `cd frontend && npm run build` |
| تست چاپگر | `cd src-tauri && cargo test` |
| migration جدید | `cd backend && .venv/bin/alembic revision --autogenerate -m "توضیح"` |

## تغییر در API (گردش کار الزامی)

1. endpoint یا schema را در `backend/app/` تغییر دهید.
2. قرارداد را بازتولید کنید:
   ```bash
   cd backend  && .venv/bin/python scripts/export_openapi.py     # docs/openapi.json
   cd frontend && npm run gen:api && npm run typecheck            # api-schema.d.ts
   ```
3. `docs/API.md` را به‌روز کنید.
4. `pytest` را اجرا کنید؛ `test_contract.py` ناهماهنگی `openapi.json`، `API.md` و کد را می‌گیرد، و CI ناهماهنگی `api-schema.d.ts` را.

## تغییر در UI

- همه‌ی اندازه‌ها `rem` باشند، نه `px` (به‌جز خطوط ظریف و حداقل ناحیه‌ی لمس).
- قاعده‌ی مخصوص یک چیدمان را با `.shell[data-layout="…"]` (و در صورت نیاز `[data-step="…"]`) محدود کنید؛ تغییر برای عمودی نباید افقی را تغییر دهد.
- حداقل ناحیه‌ی لمس: ۴۴px. ردیف‌ها و دکمه‌ها روی کیوسک بزرگ‌تر هستند (`--tap`).
- نوشتن رنگ مستقیم ممنوع؛ از توکن‌های CSS (`--ink`, `--accent`, `--surface` …) استفاده کنید تا حالت تیره کار کند.
- هر مودال از `ModalDialog` استفاده کند (تله‌ی فوکوس، Escape، بازگرداندن فوکوس).
- بعد از تغییر ظاهری، هر سه ابعاد مرجع (۱۲۸۰×۸۰۰، ۸۰۰×۱۲۸۰، ۳۹۰×۸۴۴) و یک ابعاد کوچک (۳۶۰×۶۴۰) را در مرورگر ببینید. دکمه‌ی «نمای طراحی» در حالت dev کمک می‌کند.

## فونت‌ها و برند

| دارایی | مسیر |
|---|---|
| میخک (متغیر، ارقام فارسی) — فونت اصلی | `frontend/src/assets/fonts/Mikhak-FD.woff2` |
| A Ghasem — فقط لوگوتایپ | `frontend/src/assets/fonts/AGhasem.woff2` |
| لوگو / favicon | `frontend/public/logo.png`, `favicon.png` |
| آیکن برنامه‌ی دسکتاپ | `src-tauri/app-icon.png` (۱۰۲۴px؛ با `npm run icons` به همه‌ی اندازه‌ها تبدیل می‌شود) |

لوگوتایپ دو ردیف عمودی است: «کلینیک فوق تخصصی» بالا و «نوین دیدگان» پایین (کامپوننت `BrandMark.vue`).
مجوز فونت‌ها را پیش از انتشار عمومی مخزن بررسی کنید.

## CI

`.github/workflows/ci.yml` روی هر push/PR: تست بک‌اند (شامل قرارداد) ← بازتولید تایپ‌های API و مقایسه ← typecheck، تست و build فرانت.
