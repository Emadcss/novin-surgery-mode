import { barcodeBars, barcodeWidth } from './barcode'
import { fa, fmtCode } from './fa'
import { isoJText, timeText } from './jalali'
import { PROCS } from './labels'
import type { Appointment } from './types'

/** عرض ۸۰ میلی‌متر در ۲۰۳ نقطه‌بر‌اینچ */
export const RECEIPT_WIDTH = 576

export interface ReceiptRow { label: string; value: string }

export function receiptRows(ap: Appointment): ReceiptRow[] {
  return [
    { label: 'بیمار', value: `${ap.first_name} ${ap.last_name}` },
    { label: 'عمل', value: PROCS[ap.procedure].name },
    { label: 'پزشک', value: ap.doctor_name },
    { label: 'تاریخ', value: isoJText(ap.visit_date) },
    { label: 'ساعت', value: timeText(ap.created_at) },
    { label: 'سابقه', value: ap.has_history ? 'دارد' : 'ندارد' },
    { label: 'نوبت امروز', value: fa(ap.seq) },
  ]
}

/**
 * قبض را روی بوم رسم می‌کند و PNG (بدون پیشوند data:) برمی‌گرداند.
 * چاپگرهای حرارتی معمولاً فونت فارسی ندارند، بنابراین تصویر چاپ می‌شود.
 */
export async function renderReceiptPng(ap: Appointment): Promise<string> {
  await Promise.all([document.fonts.load('700 30px Vazirmatn'), document.fonts.load('500 24px Vazirmatn'), document.fonts.load('700 56px "IBM Plex Sans Arabic"')])
  const W = RECEIPT_WIDTH
  const pad = 28
  const rows = receiptRows(ap)
  const H = 150 + 190 + rows.length * 46 + 150 + 120
  const c = document.createElement('canvas')
  c.width = W
  c.height = H
  const ctx = c.getContext('2d')!
  ctx.fillStyle = '#fff'
  ctx.fillRect(0, 0, W, H)
  ctx.fillStyle = '#000'
  ctx.textBaseline = 'alphabetic'
  let y = 56
  const center = (text: string, font: string, dir: CanvasDirection = 'rtl') => {
    ctx.font = font; ctx.direction = dir; ctx.textAlign = 'center'
    ctx.fillText(text, W / 2, y)
  }
  const rule = () => {
    ctx.save(); ctx.setLineDash([6, 6]); ctx.lineWidth = 2
    ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(W - pad, y); ctx.stroke(); ctx.restore()
  }

  center('نوین دیدگان', '800 40px Vazirmatn'); y += 40
  center('قبض پذیرش جراحی', '500 26px Vazirmatn'); y += 28
  rule(); y += 44
  center('کد پذیرش', '500 24px Vazirmatn'); y += 62
  center(fa(fmtCode(ap.code)), '700 56px "IBM Plex Sans Arabic"', 'ltr'); y += 52
  rule(); y += 42
  for (const r of rows) {
    ctx.font = '500 26px Vazirmatn'; ctx.direction = 'rtl'; ctx.textAlign = 'right'
    ctx.fillText(r.label, W - pad, y)
    ctx.font = '700 28px Vazirmatn'; ctx.textAlign = 'left'
    ctx.fillText(r.value, pad, y)
    y += 46
  }
  y -= 8
  rule(); y += 24
  const bars = barcodeBars(ap.code)
  const bw = barcodeWidth(bars)
  const k = (W - pad * 2) / bw
  for (const b of bars) ctx.fillRect(pad + b.x * k, y, Math.max(1, b.w * k), 70)
  y += 70 + 40
  center('تخصص ‑ پزشک ‑ ماه‌و‌روز ‑ سابقه ‑ شماره نوبت', '500 20px Vazirmatn'); y += 40
  center('این قبض را به میز پذیرش تحویل دهید.', '600 24px Vazirmatn')
  return c.toDataURL('image/png').split(',')[1]!
}
