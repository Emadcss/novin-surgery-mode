/**
 * فهرست متن‌های قابل ویرایش کیوسک. مقدار پیش‌فرض اینجاست؛ ادمین از «تنظیمات ← متن‌های کیوسک» هر کدام را
 * تغییر می‌دهد و فقط مقدارهای تغییرکرده در دیتابیس ذخیره می‌شوند. `{name}` در متن با نام بیمار جایگزین می‌شود.
 */
export interface TextDef { key: string; group: string; label: string; def: string; long?: boolean; vars?: string[] }

export const TEXT_GROUPS = ['صفحه‌ی اول', 'مراحل (عنوان و راهنما)', 'کارت‌ها', 'بازبینی', 'پایان پذیرش'] as const

export const TEXT_DEFS: TextDef[] = [
  { key: 'welcome.eyebrow', group: 'صفحه‌ی اول', label: 'برچسب بالای تیتر', def: 'پذیرش خودکار جراحی' },
  { key: 'welcome.body', group: 'صفحه‌ی اول', label: 'توضیح زیر تیتر', long: true, def: 'در چند مرحله‌ی کوتاه، نوع عمل و پزشک را انتخاب کنید، مشخصاتتان را وارد کنید و کد پذیرش و قبض را همراه ببرید.' },
  { key: 'welcome.p1', group: 'صفحه‌ی اول', label: 'نکته‌ی اول (کنار دکمه)', def: 'حدود ۲ دقیقه' },
  { key: 'welcome.p2', group: 'صفحه‌ی اول', label: 'نکته‌ی دوم (کنار دکمه)', def: 'اطلاعات شما محرمانه می‌ماند' },

  { key: 'step.cat.title', group: 'مراحل (عنوان و راهنما)', label: 'نوع جراحی — عنوان', def: 'نوع جراحی را انتخاب کنید' },
  { key: 'step.cat.hint', group: 'مراحل (عنوان و راهنما)', label: 'نوع جراحی — راهنما', def: 'یکی از دو گزینه را لمس کنید' },
  { key: 'step.proc.title', group: 'مراحل (عنوان و راهنما)', label: 'نوع عمل چشم — عنوان', def: 'نوع عمل چشم را انتخاب کنید' },
  { key: 'step.proc.hint', group: 'مراحل (عنوان و راهنما)', label: 'نوع عمل چشم — راهنما', def: 'تزریق چشمی یا جراحی چشمی' },
  { key: 'step.doctor.title', group: 'مراحل (عنوان و راهنما)', label: 'پزشک — عنوان', def: 'پزشک خود را انتخاب کنید' },
  { key: 'step.doctor.hint', group: 'مراحل (عنوان و راهنما)', label: 'پزشک — راهنما', def: 'پزشک مورد نظر را لمس کنید' },
  { key: 'step.name.title', group: 'مراحل (عنوان و راهنما)', label: 'نام — عنوان', def: 'نام و نام خانوادگی' },
  { key: 'step.name.hint', group: 'مراحل (عنوان و راهنما)', label: 'نام — راهنما', def: 'نام و نام خانوادگی خود را فارسی وارد کنید' },
  { key: 'step.mobile.title', group: 'مراحل (عنوان و راهنما)', label: 'موبایل — عنوان', def: 'شماره موبایل شما' },
  { key: 'step.mobile.hint', group: 'مراحل (عنوان و راهنما)', label: 'موبایل — راهنما', def: 'شماره باید با ۰۹ شروع شود و ۱۱ رقم باشد' },
  { key: 'step.history.title', group: 'مراحل (عنوان و راهنما)', label: 'سابقه — عنوان', def: 'قبلاً در این مرکز جراحی داشته‌اید؟' },
  { key: 'step.history.hint', group: 'مراحل (عنوان و راهنما)', label: 'سابقه — راهنما', def: 'پاسخ شما در پرونده ثبت می‌شود' },
  { key: 'step.review.title', group: 'مراحل (عنوان و راهنما)', label: 'بازبینی — عنوان', def: 'اطلاعات را بررسی کنید' },
  { key: 'step.review.hint', group: 'مراحل (عنوان و راهنما)', label: 'بازبینی — راهنما', def: '' },

  { key: 'card.cat.eye.sub', group: 'کارت‌ها', label: 'کارت جراحی چشم — توضیح', def: 'تزریق چشمی یا جراحی چشمی' },
  { key: 'card.cat.cos.sub', group: 'کارت‌ها', label: 'کارت جراحی زیبایی — توضیح', def: 'انتخاب پزشک جراحی زیبایی' },
  { key: 'card.proc.inj_eye.sub', group: 'کارت‌ها', label: 'کارت تزریق چشمی — توضیح', def: 'تزریق دارو داخل چشم' },
  { key: 'card.proc.surg_eye.sub', group: 'کارت‌ها', label: 'کارت جراحی چشمی — توضیح', def: 'مانند آب‌مروارید، لیزیک و جراحی پلک' },
  { key: 'card.history.yes', group: 'کارت‌ها', label: 'سابقه: «بله» — عنوان', def: 'بله، قبلاً جراحی داشته‌ام' },
  { key: 'card.history.yes.sub', group: 'کارت‌ها', label: 'سابقه: «بله» — توضیح', def: 'در این مرکز پرونده دارم' },
  { key: 'card.history.no', group: 'کارت‌ها', label: 'سابقه: «خیر» — عنوان', def: 'خیر، اولین بار است' },
  { key: 'card.history.no.sub', group: 'کارت‌ها', label: 'سابقه: «خیر» — توضیح', def: 'پرونده‌ی جدید برای شما ساخته می‌شود' },
  { key: 'doctor.empty', group: 'کارت‌ها', label: 'وقتی پزشکی فعال نیست', long: true, def: 'در حال حاضر پزشکی برای این بخش فعال نیست. لطفاً به میز پذیرش مراجعه کنید.' },

  { key: 'review.note', group: 'بازبینی', label: 'یادآوری اصلاح اطلاعات', long: true, def: 'اطلاعات خود را در پرونده بررسی کنید. برای اصلاح هر بخش، همان خط را لمس کنید.' },
  { key: 'review.consent', group: 'بازبینی', label: 'متن کنار دکمه‌ی تأیید', long: true, def: 'با تأیید، اطلاعات شما برای پذیرش جراحی ثبت می‌شود و کد پذیرش و قبض صادر خواهد شد.' },

  { key: 'done.title', group: 'پایان پذیرش', label: 'برچسب بالای کد', def: 'پذیرش شما ثبت شد' },
  { key: 'done.step1', group: 'پایان پذیرش', label: 'گام اول', def: 'قبض چاپ‌شده را بردارید.' },
  { key: 'done.wait', group: 'پایان پذیرش', label: 'پیام انتظار', long: true, vars: ['name'], def: '{name} عزیز، منتظر بمانید تا همکاران پذیرش نام شما را اعلام کنند.' },
  { key: 'done.form', group: 'پایان پذیرش', label: 'پیام بیمار بدون سابقه', long: true, def: 'لطفاً فرم مشخصات شخصی را تکمیل فرمایید.' },
  { key: 'receipt.footer', group: 'پایان پذیرش', label: 'متن پایین قبض چاپی', long: true, vars: ['name'], def: '{name} عزیز، لطفاً منتظر بمانید تا همکاران پذیرش نام شما را اعلام کنند.' },
]

export const TEXT_DEFAULTS: Record<string, string> = Object.fromEntries(TEXT_DEFS.map((d) => [d.key, d.def]))
export const TEXT_MAX = 300
