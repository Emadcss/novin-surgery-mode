# راهنمای استقرار

دو بخش جدا: **سرور** (دیتابیس + API) و **کیوسک** (برنامه‌ی Tauri روی رایانه‌ی نمایشگر لمسی).

## ۱) سرور

### با Docker Compose (پیشنهادی)

```bash
cp .env.example .env
```
مقادیر `.env`:

| متغیر | توضیح |
|---|---|
| `POSTGRES_PASSWORD` | رمز دیتابیس — **حتماً تغییر دهید** |
| `SECRET_KEY` | کلید امضای JWT — الزامی؛ `openssl rand -hex 32` |
| `KIOSK_KEY` | اگر پر شود، کیوسک‌ها باید همین را در هدر `X-Kiosk-Key` بفرستند (توصیه می‌شود) |
| `SEED_ADMIN_PIN` | PIN چهار رقمی ادمین اولیه — بعد از اولین ورود تغییرش دهید یا ادمین جدید بسازید |

```bash
docker compose up -d --build
```
- هنگام راه‌اندازی، API خودکار `alembic upgrade head` و `python -m app.seed` را اجرا می‌کند (ادمین و پزشکان نمونه فقط در صورت خالی‌بودن جدول ساخته می‌شوند).
- API روی پورت `8000`؛ دیتابیس روی `5432` (در سرور واقعی پورت دیتابیس را از `docker-compose.yml` حذف کنید یا با فایروال ببندید).
- داده‌ها در volumeهای `pgdata` (دیتابیس) و `media` (عکس پزشکان) می‌مانند.

### پشت reverse proxy و HTTPS

API را پشت nginx/Caddy با TLS قرار دهید. نمونه‌ی Caddy:

```
kiosk.example.ir {
    reverse_proxy 127.0.0.1:8000
}
```
اگر کیوسک و پنل از دامنه‌ی دیگری باز می‌شوند، همان origin را در `CORS_ORIGINS` (آرایه‌ی JSON) اضافه کنید.

### بدون Docker

```bash
cd backend && pip install . 
export DATABASE_URL=postgresql+psycopg://USER:PASS@HOST:5432/novin_kiosk SECRET_KEY=... KIOSK_KEY=... MEDIA_DIR=/var/lib/novin/media
alembic upgrade head && python -m app.seed
uvicorn app.main:app --host 0.0.0.0 --port 8000        # یا با systemd
```

### پشتیبان‌گیری

```bash
docker compose exec db pg_dump -U novin novin_kiosk | gzip > backup-$(date +%F).sql.gz   # دیتابیس
docker run --rm -v novin-kiosk_media:/m -v "$PWD":/b alpine tar czf /b/media-$(date +%F).tgz -C /m .   # عکس‌ها
```
پشتیبان روزانه و آزمون دوره‌ای بازیابی توصیه می‌شود (داده شامل نام و موبایل بیماران است).

### به‌روزرسانی

```bash
git pull && docker compose up -d --build        # migrationها خودکار اجرا می‌شوند
```

## ۲) کیوسک (Tauri)

### ساخت نصب‌کننده
پیش‌نیاز: Node ۲۲، Rust و [وابستگی‌های Tauri](https://tauri.app/start/prerequisites/) برای سیستم‌عامل مقصد. روی هر سیستم‌عامل برای همان سیستم‌عامل بسازید.

```bash
npm i && npm run icons
npm run build            # خروجی: src-tauri/target/release/bundle/ (NSIS برای ویندوز، deb/AppImage برای لینوکس)
```

### پیکربندی روی دستگاه کیوسک

فایل `kiosk.config.json` را **کنار فایل اجرایی** بگذارید (یا مسیر آن را در متغیر محیطی `KIOSK_CONFIG` بدهید):

```json
{
  "api_base": "https://kiosk.example.ir",
  "kiosk_key": "همان KIOSK_KEY سرور",
  "printer": "tcp:192.168.1.50:9100"
}
```

| مقدار `printer` | کاربرد |
|---|---|
| `tcp:IP:9100` | چاپگر شبکه‌ای (پیشنهادی) |
| `\\localhost\Receipt` | چاپگر اشتراکی ویندوز (نام اشتراک) |
| `\\.\USB001` | پورت USB ویندوز |
| `/dev/usb/lp0` | لینوکس |

### چاپگر
- چاپگر حرارتی ۸۰mm سازگار با **ESC/POS** (عرض ۵۷۶ نقطه)؛ نیازی به فونت فارسی در چاپگر نیست چون قبض تصویر است.
- بعد از نصب، یک نوبت آزمایشی ثبت کنید و چاپ را بررسی کنید. اگر چاپ شکست بخورد، کیوسک کد پذیرش را روی صفحه نشان می‌دهد و پیام خطا می‌دهد.

### حالت کیوسک
- برنامه تمام‌صفحه و بدون قاب باز می‌شود. برای قفل‌کردن سیستم‌عامل روی همین برنامه از امکانات خود OS استفاده کنید (ویندوز: Assigned Access/Kiosk mode؛ لینوکس: ورود خودکار کاربر محدود + autostart).
- برنامه را در autostart قرار دهید و نمایش خواب/محافظ صفحه را غیرفعال کنید.
- ورود مدیر روی کیوسک: ۵ لمس پشت‌سرهم روی لوگو. اگر نمی‌خواهید بیمار به این مسیر دسترسی داشته باشد، PIN ادمین را قوی و محرمانه نگه دارید.

## چک‌لیست قبل از راه‌اندازی

- [ ] `SECRET_KEY` تصادفی، `POSTGRES_PASSWORD` و `KIOSK_KEY` تنظیم شده‌اند
- [ ] PIN پیش‌فرض ادمین (`1234`) عوض شده است
- [ ] HTTPS برقرار است و پورت دیتابیس از بیرون بسته است
- [ ] پشتیبان‌گیری زمان‌بندی شده است
- [ ] زمان سرور و منطقه‌ی زمانی درست است (`TIMEZONE=Asia/Tehran`؛ شماره‌ی نوبت و تاریخ شمسی کد بر آن اساس است)
- [ ] چاپ آزمایشی موفق بود و پزشکان واقعی ثبت شده‌اند (پزشکان نمونه را حذف یا ویرایش کنید)
- [ ] ماندن حالت روشن (پیش‌فرض) تأیید شد؛ حالت تیره فقط در صورت نیاز از تنظیمات
