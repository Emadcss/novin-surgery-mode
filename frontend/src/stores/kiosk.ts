import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { ApiError, api } from '../lib/api'
import { fa, fmtMobile } from '../lib/fa'
import { CATS, PROCS } from '../lib/labels'
import type { Appointment, Category, KioskDoctor, Procedure } from '../lib/types'
import { mobOk, nameOk } from '../lib/validators'

export type StepId = 'cat' | 'proc' | 'doctor' | 'name' | 'mobile' | 'history' | 'review'
export type Screen = 'welcome' | 'flow' | 'saving' | 'fail' | 'done'

export const STEPS: { id: StepId; title: string; hint: string }[] = [
  { id: 'cat', title: 'نوع جراحی را انتخاب کنید', hint: 'یکی از دو گروه را لمس کنید' },
  { id: 'proc', title: 'کدام نوع؟', hint: 'یکی را لمس کنید' },
  { id: 'doctor', title: 'پزشک خود را انتخاب کنید', hint: 'پزشکان این بخش نمایش داده می‌شوند' },
  { id: 'name', title: 'نام و نام خانوادگی', hint: 'با کیبورد فارسی وارد کنید' },
  { id: 'mobile', title: 'شماره موبایل شما', hint: 'نوبت و یادآوری به این شماره پیامک می‌شود' },
  { id: 'history', title: 'قبلاً در این مرکز جراحی داشته‌اید؟', hint: 'این پاسخ در پرونده شما ثبت می‌شود' },
  { id: 'review', title: 'پرونده را بررسی کنید', hint: '' },
]
const stepIdx = (id: StepId) => STEPS.findIndex((s) => s.id === id)

export interface DossierLine { f: 'proc' | 'doctor' | 'first' | 'last' | 'mobile' | 'history'; step: StepId; lbl: string }
export const LINES: DossierLine[] = [
  { f: 'proc', step: 'proc', lbl: 'نوع جراحی' },
  { f: 'doctor', step: 'doctor', lbl: 'پزشک' },
  { f: 'first', step: 'name', lbl: 'نام' },
  { f: 'last', step: 'name', lbl: 'نام خانوادگی' },
  { f: 'mobile', step: 'mobile', lbl: 'موبایل' },
  { f: 'history', step: 'history', lbl: 'سابقه جراحی در مرکز' },
]

export const useKiosk = defineStore('kiosk', () => {
  const screen = ref<Screen>('welcome')
  const step = ref<StepId>('cat')
  const cat = ref<Category | null>(null)
  const proc = ref<Procedure | null>(null)
  const doctorId = ref<number | null>(null)
  const doctors = ref<KioskDoctor[]>([])
  const doctorsState = ref<'idle' | 'loading' | 'error' | 'ready'>('idle')
  const first = ref('')
  const last = ref('')
  const mobile = ref('')
  const history = ref<boolean | null>(null)
  const activeName = ref<'first' | 'last'>('first')
  const reached = ref(0)
  const backToReview = ref(false)
  const record = ref<Appointment | null>(null)
  const error = ref('')

  const visible = computed(() => STEPS.filter((s) => s.id !== 'proc' || cat.value === 'eye'))
  const position = computed(() => visible.value.findIndex((s) => s.id === step.value))
  const doctor = computed(() => doctors.value.find((d) => d.id === doctorId.value) ?? null)

  function valid(id: StepId): boolean {
    switch (id) {
      case 'cat': return !!cat.value
      case 'proc': return !!proc.value
      case 'doctor': return !!doctor.value
      case 'name': return nameOk(first.value) && nameOk(last.value)
      case 'mobile': return mobOk(mobile.value)
      case 'history': return history.value !== null
      default: return true
    }
  }
  const stepValid = computed(() => valid(step.value))

  function fieldText(f: DossierLine['f']): string {
    switch (f) {
      case 'proc': return proc.value ? PROCS[proc.value].name : cat.value ? CATS[cat.value].name : ''
      case 'doctor': return doctor.value?.name ?? ''
      case 'first': return first.value
      case 'last': return last.value
      case 'mobile': return mobile.value ? '\u2066' + fa(fmtMobile(mobile.value)) + '\u2069' : ''
      case 'history': return history.value === null ? '' : history.value ? 'دارد' : 'ندارد'
    }
  }
  function fieldDone(f: DossierLine['f']): boolean {
    switch (f) {
      case 'proc': return !!proc.value
      case 'doctor': return !!doctor.value
      case 'first': return nameOk(first.value)
      case 'last': return nameOk(last.value)
      case 'mobile': return mobOk(mobile.value)
      case 'history': return history.value !== null
    }
  }
  const doneCount = computed(() => LINES.filter((l) => fieldDone(l.f)).length)

  async function loadDoctors() {
    if (!proc.value) return
    doctorsState.value = 'loading'
    try {
      doctors.value = await api.kioskDoctors(proc.value)
      if (doctorId.value && !doctors.value.some((d) => d.id === doctorId.value)) doctorId.value = null
      doctorsState.value = 'ready'
    } catch {
      doctorsState.value = 'error'
    }
  }

  function go(id: StepId) {
    step.value = id
    reached.value = Math.max(reached.value, stepIdx(id))
    if (id === 'doctor') void loadDoctors()
  }
  function next() {
    if (!stepValid.value) return
    if (backToReview.value) {
      const inc = visible.value.slice(0, -1).find((s) => !valid(s.id))
      go(inc ? inc.id : 'review')
      if (!inc) backToReview.value = false
      return
    }
    go(visible.value[position.value + 1]!.id)
  }
  function back() {
    backToReview.value = false
    go(visible.value[Math.max(0, position.value - 1)]!.id)
  }
  function start() {
    reset()
    screen.value = 'flow'
  }
  function pickCat(c: Category) {
    if (cat.value !== c) { doctorId.value = null; doctors.value = []; doctorsState.value = 'idle' }
    cat.value = c
    if (c === 'cos') proc.value = 'cos'
    else if (!proc.value || PROCS[proc.value].cat !== c) proc.value = null
    setTimeout(() => { if (step.value === 'cat') next() }, 260)
  }
  function pickProc(p: Procedure) {
    if (proc.value !== p) { doctorId.value = null; doctors.value = []; doctorsState.value = 'idle' }
    proc.value = p
    setTimeout(() => { if (step.value === 'proc') next() }, 260)
  }
  function pickDoctor(id: number) {
    doctorId.value = id
    setTimeout(() => { if (step.value === 'doctor') next() }, 260)
  }
  function pickHistory(v: boolean) {
    history.value = v
    setTimeout(() => { if (step.value === 'history') next() }, 260)
  }
  /** لمس یک خط پرونده برای ویرایش */
  function edit(target: StepId, field?: string) {
    backToReview.value = reached.value >= stepIdx('review')
    step.value = target === 'proc' && cat.value !== 'eye' ? 'cat' : target
    if (step.value === 'name') activeName.value = field === 'last' ? 'last' : 'first'
    if (step.value === 'doctor') void loadDoctors()
  }
  function canEdit(line: DossierLine): boolean {
    return screen.value === 'flow' && stepIdx(line.step) <= reached.value && line.step !== step.value && fieldDone(line.f)
  }

  async function confirm() {
    if (!proc.value || !doctorId.value) return
    screen.value = 'saving'
    error.value = ''
    const t0 = Date.now()
    try {
      const ap = await api.kioskBook({
        procedure: proc.value, doctor_id: doctorId.value, first_name: first.value.trim(), last_name: last.value.trim(),
        mobile: mobile.value, has_history: !!history.value,
      })
      await new Promise((r) => setTimeout(r, Math.max(0, 1200 - (Date.now() - t0))))
      record.value = ap
      screen.value = 'done'
    } catch (e) {
      await new Promise((r) => setTimeout(r, Math.max(0, 900 - (Date.now() - t0))))
      error.value = e instanceof ApiError ? e.message : 'خطای ناشناخته'
      // اگر پزشک دیگر در دسترس نیست باید دوباره انتخاب شود
      if (e instanceof ApiError && e.status === 409) { doctorId.value = null; doctorsState.value = 'idle' }
      screen.value = 'fail'
    }
  }
  function backToFlow() {
    screen.value = 'flow'
    if (!doctorId.value) { backToReview.value = true; go('doctor') } else step.value = 'review'
  }

  function reset() {
    screen.value = 'welcome'; step.value = 'cat'; cat.value = null; proc.value = null; doctorId.value = null
    doctors.value = []; doctorsState.value = 'idle'; first.value = ''; last.value = ''; mobile.value = ''
    history.value = null; activeName.value = 'first'; reached.value = 0; backToReview.value = false
    record.value = null; error.value = ''
  }

  return {
    screen, step, cat, proc, doctorId, doctors, doctorsState, first, last, mobile, history, activeName, reached,
    backToReview, record, error, visible, position, doctor, stepValid, doneCount,
    valid, fieldText, fieldDone, loadDoctors, go, next, back, start, pickCat, pickProc, pickDoctor, pickHistory,
    edit, canEdit, confirm, backToFlow, reset,
  }
})
