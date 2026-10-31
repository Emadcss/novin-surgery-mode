import { fa, pad2 } from './fa'

export const MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
export const WEEKDAYS = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']

export interface J { y: number; m: number; d: number }

const JF = new Intl.DateTimeFormat('en-u-ca-persian-nu-latn', { year: 'numeric', month: 'numeric', day: 'numeric', timeZone: 'UTC' })
const TEHRAN_DATE = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Tehran', year: 'numeric', month: '2-digit', day: '2-digit' })
const TEHRAN_TIME = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Tehran', hour: '2-digit', minute: '2-digit', hour12: false })

const DAY = 864e5

/** تاریخ میلادی (ساعت ۱۲ UTC) → شمسی */
export function jp(d: Date): J {
  const p = JF.formatToParts(d)
  const g = (t: string) => +p.find((x) => x.type === t)!.value
  return { y: g('year'), m: g('month'), d: g('day') }
}

const jkey = (y: number, m: number, d: number) => y * 10000 + m * 100 + d

/** تاریخ شمسی → Date (ساعت ۱۲ UTC) */
export function jToDate(y: number, m: number, d: number): Date {
  let t = new Date(Date.UTC(y + 621, 2, 21, 12) + Math.floor((m - 1) * 30.5 + (d - 1)) * DAY)
  const key = jkey(y, m, d)
  for (let i = 0; i < 80; i++) {
    const p = jp(t)
    const k = jkey(p.y, p.m, p.d)
    if (k === key) return t
    t = new Date(t.getTime() + (k < key ? 1 : -1) * DAY)
  }
  return t
}

export function monthLen(y: number, m: number): number {
  const a = jToDate(y, m, 1)
  const b = m === 12 ? jToDate(y + 1, 1, 1) : jToDate(y, m + 1, 1)
  return Math.round((b.getTime() - a.getTime()) / DAY)
}

/** «امروز» به وقت تهران، به‌صورت Date ساعت ۱۲ UTC */
export function today(): Date {
  return isoToDate(TEHRAN_DATE.format(new Date()))
}

export const isoToDate = (iso: string): Date => {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(Date.UTC(y!, m! - 1, d!, 12))
}
export const dateToIso = (d: Date): string => d.toISOString().slice(0, 10)
export const addDays = (d: Date, n: number): Date => new Date(d.getTime() + n * DAY)
export const diffDays = (a: Date, b: Date): number => Math.round((a.getTime() - b.getTime()) / DAY)

export const jText = (j: J): string => `${fa(j.d)} ${MONTHS[j.m - 1]} ${fa(j.y)}`
export const isoJText = (iso: string): string => jText(jp(isoToDate(iso)))
export const dayShort = (iso: string): string => fa(jp(isoToDate(iso)).d)

/** ساعت به وقت تهران از رشته‌ی ISO سرور */
export const timeText = (iso: string | Date = new Date()): string => fa(TEHRAN_TIME.format(typeof iso === 'string' ? new Date(iso) : iso))

/** ماه و روز شمسی با دو رقم، مثلاً «۰۸۰۶» */
export const jMMDD = (j: J): string => pad2(j.m) + pad2(j.d)
