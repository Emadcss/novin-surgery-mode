# قرارداد API — کیوسک پذیرش جراحی

پایه: `/api` — JSON با UTF-8 — خطاها: `{"detail": "..."}` با کد 4xx.
تاریخ‌ها میلادی ISO هستند. تبدیل به شمسی در فرانت انجام می‌شود، به‌جز **کد پذیرش** که سرور با ماه و روز شمسی می‌سازد.

## Enumها
| نام | مقادیر |
|---|---|
| `category` | `eye` (جراحی چشم), `cos` (جراحی زیبایی) |
| `procedure` | `inj_eye` (تزریق چشمی), `surg_eye` (جراحی چشمی), `cos` (جراحی زیبایی؛ زیرمجموعه ندارد) |
| `status` | `booked`, `done`, `cancelled` |

## کیوسک (هدر اختیاری `X-Kiosk-Key` اگر در سرور تنظیم شده باشد)
- `GET /api/kiosk/doctors?category=eye|cos&procedure=inj_eye|surg_eye|cos`
  فقط پزشکان فعال و حذف‌نشده. برای `procedure=inj_eye` فقط پزشکانی با `does_injection=true`.
  → `[{id, name, role, category, does_injection, photo_url|null, today_count}]`
- `POST /api/kiosk/appointments`
  `{procedure, doctor_id, first_name, last_name, mobile, has_history}` → `201 Appointment`
  اعتبارسنجی: پزشک فعال و هم‌گروه با عمل (و اگر `inj_eye` است دارای تزریق)، نام فارسی ۲ تا ۲۴ حرف، موبایل `^09\d{9}$` (ارقام فارسی/عربی نرمال می‌شوند).
  `422` برای ورودی نامعتبر، `409` اگر پزشک دیگر در دسترس نیست.

### Appointment
`{id, code, seq, procedure, category, doctor_id, doctor_name, first_name, last_name, mobile, has_history, status, visit_date, created_at}`
- `code`: ۱۱ رقم = `[گروه ۱|۲][شماره پزشک ۲ رقم][ماه‌روز شمسی ۴ رقم][سابقه ۰|۱][شماره نوبت روز ۳ رقم]`
- `seq`: شماره نوبت همان روز (به وقت تهران)، یکتا در هر روز.

## احراز هویت ادمین
- `POST /api/auth/login` `{pin}` → `{access_token, token_type:"bearer", admin:{id,name}}`; `401` رمز اشتباه، `429` پس از ۵ تلاش ناموفق (قفل ۵ دقیقه‌ای بر اساس IP).
- همه‌ی `/api/admin/*` نیاز به `Authorization: Bearer <token>` دارند.
- `GET /api/admin/me` → `{id,name}`

## پزشکان (ادمین)
- `GET /api/admin/doctors` → `[Doctor]` (شامل غیرفعال‌ها)
- `POST /api/admin/doctors` `{name, role?, category, does_injection=true, is_active=true}` → `201 Doctor`
- `PATCH /api/admin/doctors/{id}` هر زیرمجموعه از همان فیلدها
- `DELETE /api/admin/doctors/{id}` حذف نرم (نوبت‌های قبلی با نام ثبت‌شده باقی می‌مانند) → `204`
- `POST /api/admin/doctors/{id}/photo` (multipart، فیلد `file`) → `Doctor` — سرور مربع‌برش و فشرده می‌کند (۳۲۰×۳۲۰ JPEG)
- `DELETE /api/admin/doctors/{id}/photo` → `Doctor`
- `Doctor`: `{id, no, name, role, category, does_injection, is_active, photo_url, today_count, total_count}`
  برای `category=cos` مقدار `does_injection` همیشه `false` است.

## نوبت‌ها (ادمین)
- `GET /api/admin/appointments?q&category&status&doctor_id&date_from&date_to&limit=100&offset=0` → `{items:[Appointment], total}`
  `q` روی نام، موبایل و کد جستجو می‌کند. مرتب‌سازی: جدیدترین اول.
- `PATCH /api/admin/appointments/{id}` `{status}` → `Appointment`
- `DELETE /api/admin/appointments/{id}` → `204`

## بیماران (ادمین)
- `GET /api/admin/patients?q&limit=100&offset=0` → `{items:[{mobile, first_name, last_name, appointments_count, last_visit_date, appointments:[Appointment]}], total}`
  بیمار با موبایل شناسایی می‌شود؛ نام از آخرین نوبت.

## آمار (ادمین)
- `GET /api/admin/stats/dashboard` → `{today:{total,booked,done,cancelled}, total_appointments, total_patients, history_count, active_doctors, total_doctors, last7:[{date,count}]}`
- `GET /api/admin/stats/calendar?date_from&date_to` → `[{date,count}]`
- `GET /api/admin/stats/report?days=7|30|0` (۰ یعنی همه) → `{total, done, cancelled, with_history, per_day:[{date,count}], by_category:[{key,count}], by_procedure:[{key,count}], by_doctor:[{key,count}]}`
  `per_day` برای `days=30` سی روز اخیر و در غیر این صورت چهارده روز اخیر؛ `by_*` نوبت‌های لغوشده را حساب نمی‌کند.

## ادمین‌ها
- `GET /api/admin/admins` → `[{id,name}]`
- `POST /api/admin/admins` `{name, pin}` (pin چهار رقم؛ `409` اگر تکراری)
- `PATCH /api/admin/admins/{id}` `{name?, pin?}`
- `DELETE /api/admin/admins/{id}` (`400` برای حذف خود یا تنها ادمین)

## تنظیمات
- `GET /api/kiosk/settings` → `{theme}` (با `X-Kiosk-Key` اگر تنظیم شده)
- `GET /api/admin/settings` → `{theme}`؛ `PATCH /api/admin/settings` `{theme?}` → `{theme}`
- `theme`: `light` (پیش‌فرض) | `dark` | `auto`. حالت تیره فقط با انتخاب ادمین فعال می‌شود؛ `422` برای مقدار نامعتبر.

## سایر
- `GET /api/health` → `{status:"ok"}`
- فایل‌های ثابت: `GET /media/doctors/<file>.jpg`

## منبع حقیقت و بررسی خودکار
مشخصات ماشین‌خوان در `docs/openapi.json` ذخیره است و از خود FastAPI ساخته می‌شود:
```bash
cd backend && .venv/bin/python scripts/export_openapi.py        # بازسازی docs/openapi.json
cd frontend && npm run gen:api                                  # ساخت src/lib/api-schema.d.ts از روی آن
```
- تست `tests/test_contract.py` اگر `docs/openapi.json` با کد هم‌خوان نباشد یا مسیری در این سند نیامده باشد شکست می‌خورد.
- فرانت با `npm run typecheck` تطابق تایپ‌های دستی (`lib/types.ts`) را با `api-schema.d.ts` می‌سنجد.
