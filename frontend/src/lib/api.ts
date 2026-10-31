import { config } from './config'
import type {
  AdminUser, Appointment, Settings, Theme, AppointmentIn, Dashboard, DayCount, Doctor, DoctorIn, KioskDoctor, Page, Patient, Procedure, Report, Status,
} from './types'

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

let token: string | null = null
let onUnauthorized: () => void = () => {}
export const setToken = (t: string | null) => { token = t }
export const setUnauthorizedHandler = (fn: () => void) => { onUnauthorized = fn }

type Q = Record<string, string | number | boolean | null | undefined>

async function request<T>(method: string, path: string, opts: { query?: Q; body?: unknown; form?: FormData; kiosk?: boolean } = {}): Promise<T> {
  const url = new URL(`${config.apiBase}/api${path}`, window.location.origin)
  for (const [k, v] of Object.entries(opts.query ?? {})) if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, String(v))
  const headers: Record<string, string> = {}
  if (opts.body !== undefined) headers['Content-Type'] = 'application/json'
  if (opts.kiosk && config.kioskKey) headers['X-Kiosk-Key'] = config.kioskKey
  if (token) headers.Authorization = `Bearer ${token}`
  let res: Response
  try {
    res = await fetch(url, { method, headers, body: opts.form ?? (opts.body !== undefined ? JSON.stringify(opts.body) : undefined) })
  } catch {
    throw new ApiError(0, 'ارتباط با سرور برقرار نشد')
  }
  if (res.status === 204) return undefined as T
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    if (res.status === 401 && token) onUnauthorized()
    const d = data?.detail
    const msg = typeof d === 'string' ? d : Array.isArray(d) ? (d[0]?.msg ?? 'ورودی نامعتبر است').replace(/^Value error, /, '') : 'خطای ناشناخته از سرور'
    throw new ApiError(res.status, msg)
  }
  return data as T
}

export const api = {
  // ---- کیوسک ----
  kioskDoctors: (procedure: Procedure) => request<KioskDoctor[]>('GET', '/kiosk/doctors', { query: { procedure }, kiosk: true }),
  kioskBook: (body: AppointmentIn) => request<Appointment>('POST', '/kiosk/appointments', { body, kiosk: true }),
  kioskSettings: () => request<Settings>('GET', '/kiosk/settings', { kiosk: true }),
  // ---- ورود ----
  login: (pin: string) => request<{ access_token: string; admin: AdminUser }>('POST', '/auth/login', { body: { pin } }),
  me: () => request<AdminUser>('GET', '/admin/me'),
  // ---- پزشکان ----
  doctors: () => request<Doctor[]>('GET', '/admin/doctors'),
  createDoctor: (body: DoctorIn) => request<Doctor>('POST', '/admin/doctors', { body }),
  updateDoctor: (id: number, body: Partial<DoctorIn>) => request<Doctor>('PATCH', `/admin/doctors/${id}`, { body }),
  deleteDoctor: (id: number) => request<void>('DELETE', `/admin/doctors/${id}`),
  uploadPhoto: (id: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return request<Doctor>('POST', `/admin/doctors/${id}/photo`, { form })
  },
  deletePhoto: (id: number) => request<Doctor>('DELETE', `/admin/doctors/${id}/photo`),
  // ---- نوبت‌ها ----
  appointments: (query: Q) => request<Page<Appointment>>('GET', '/admin/appointments', { query }),
  setStatus: (id: number, status: Status) => request<Appointment>('PATCH', `/admin/appointments/${id}`, { body: { status } }),
  deleteAppointment: (id: number) => request<void>('DELETE', `/admin/appointments/${id}`),
  // ---- بیماران ----
  patients: (query: Q) => request<Page<Patient>>('GET', '/admin/patients', { query }),
  // ---- آمار ----
  dashboard: () => request<Dashboard>('GET', '/admin/stats/dashboard'),
  calendar: (date_from: string, date_to: string) => request<DayCount[]>('GET', '/admin/stats/calendar', { query: { date_from, date_to } }),
  report: (days: number) => request<Report>('GET', '/admin/stats/report', { query: { days } }),
  settings: () => request<Settings>('GET', '/admin/settings'),
  setTheme: (theme: Theme) => request<Settings>('PATCH', '/admin/settings', { body: { theme } }),
  // ---- ادمین‌ها ----
  admins: () => request<AdminUser[]>('GET', '/admin/admins'),
  createAdmin: (body: { name: string; pin: string }) => request<AdminUser>('POST', '/admin/admins', { body }),
  updateAdmin: (id: number, body: { name?: string; pin?: string }) => request<AdminUser>('PATCH', `/admin/admins/${id}`, { body }),
  deleteAdmin: (id: number) => request<void>('DELETE', `/admin/admins/${id}`),
}
