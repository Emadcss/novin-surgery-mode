import type { Category, Procedure, Status } from './types'

export const CATS: Record<Category, { name: string; sub: string; icon: string }> = {
  eye: { name: 'جراحی چشم', sub: 'تزریق چشمی یا جراحی چشمی', icon: 'eye' },
  cos: { name: 'جراحی زیبایی', sub: 'مستقیم به انتخاب پزشک', icon: 'face' },
}

export const PROCS: Record<Procedure, { name: string; sub: string; icon: string; cat: Category }> = {
  inj_eye: { name: 'تزریق چشمی', sub: 'تزریق داخل چشم', icon: 'syringe', cat: 'eye' },
  surg_eye: { name: 'جراحی چشمی', sub: 'آب مروارید، لیزیک، پلک و ...', icon: 'lens', cat: 'eye' },
  cos: { name: 'جراحی زیبایی', sub: '', icon: 'spark', cat: 'cos' },
}

export const EYE_PROCS: Procedure[] = ['inj_eye', 'surg_eye']
export const STATUS: Record<Status, string> = { booked: 'ثبت‌شده', done: 'انجام‌شده', cancelled: 'لغوشده' }
export const STATUS_LIST: Status[] = ['booked', 'done', 'cancelled']
