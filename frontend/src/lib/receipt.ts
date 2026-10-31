import { barcodeBars, barcodeWidth } from './barcode'
import { fa, fmtCode } from './fa'
import { isoJText, timeText } from './jalali'
import { PROCS } from './labels'
import type { Appointment } from './types'

/** عرض ۸۰ میلی‌متر در ۲۰۳ نقطه‌بر‌اینچ */
export const RECEIPT_WIDTH = 576

/** شکستن متن فارسی به خط‌های هم‌عرض با اندازه‌گیری روی بوم */
function wrap(ctx: CanvasRenderingContext2D, text: string, font: string, max: number): string[] {
  ctx.font = font
  const out: string[] = []
  let cur = ''
  for (const w of text.split(/\s+/).filter(Boolean)) {
    const tryLine = cur ? cur + ' ' + w : w
    if (cur && ctx.measureText(tryLine).width > max) { out.push(cur); cur = w } else cur = tryLine
  }
  if (cur) out.push(cur)
  return out
}

export interface ReceiptRow { label: string; value: string }

export function receiptRows(ap: Appointment): ReceiptRow[] {
  return [
    { label: 'بیمار', value: `${ap.first_name} ${ap.last_name}` },
    { label: 'عمل', value: PROCS[ap.procedure].name },
    { label: 'پزشک', value: ap.doctor_name },
    { label: 'تاریخ', value: isoJText(ap.visit_date) },
    { label: 'ساعت', value: timeText(ap.created_at) },
    { label: 'سابقه', value: ap.has_history ? 'دارد' : 'ندارد' },
  ]
}

/**
 * قبض را روی بوم رسم می‌کند و PNG (بدون پیشوند data:) برمی‌گرداند.
 * چاپگرهای حرارتی معمولاً فونت فارسی ندارند، بنابراین تصویر چاپ می‌شود.
 */
export async function renderReceiptPng(ap: Appointment, footer = 'لطفاً منتظر بمانید تا همکاران پذیرش نام شما را اعلام کنند.'): Promise<string> {
  await Promise.all([document.fonts.load('700 30px Mikhak'), document.fonts.load('500 24px Mikhak'), document.fonts.load('700 56px Mikhak'), document.fonts.load('40px AGhasem')])
  const W = RECEIPT_WIDTH
  const pad = 28
  const rows = receiptRows(ap)
  const measure = document.createElement('canvas').getContext('2d')!
  const footLines = wrap(measure, footer, '600 24px Mikhak', W - 96)
  const H = 150 + 190 + rows.length * 46 + 150 + 30 + footLines.length * 38
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

  center('نوین دیدگان', '800 40px Mikhak'); y += 40
  center('قبض پذیرش جراحی', '500 26px Mikhak'); y += 28
  rule(); y += 44
  center('کد پذیرش', '500 24px Mikhak'); y += 62
  center(fa(fmtCode(ap.code)), '700 56px Mikhak', 'ltr'); y += 52
  rule(); y += 42
  for (const r of rows) {
    ctx.font = '500 26px Mikhak'; ctx.direction = 'rtl'; ctx.textAlign = 'right'
    ctx.fillText(r.label, W - pad, y)
    ctx.font = '700 28px Mikhak'; ctx.textAlign = 'left'
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
  for (const line of footLines) { center(line, '600 24px Mikhak'); y += 38 }
  return c.toDataURL('image/png').split(',')[1]!
}
