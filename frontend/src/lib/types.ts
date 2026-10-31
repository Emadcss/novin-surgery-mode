export type Category = 'eye' | 'cos'
export type Procedure = 'inj_eye' | 'surg_eye' | 'cos'
export type Status = 'booked' | 'done' | 'cancelled'

export interface KioskDoctor {
  id: number; name: string; role: string; category: Category
  does_injection: boolean; photo_url: string | null; today_count: number
}
export interface Appointment {
  id: number; code: string; seq: number; procedure: Procedure; category: Category
  doctor_id: number | null; doctor_name: string; first_name: string; last_name: string
  mobile: string; has_history: boolean; status: Status; visit_date: string; created_at: string
}
export interface AppointmentIn {
  procedure: Procedure; doctor_id: number; first_name: string; last_name: string; mobile: string; has_history: boolean
}
export interface Doctor {
  id: number; no: number; name: string; role: string; category: Category
  does_injection: boolean; is_active: boolean; photo_url: string | null; today_count: number; total_count: number
}
export interface DoctorIn { name: string; role: string; category: Category; does_injection: boolean; is_active: boolean }
export interface Patient {
  mobile: string; first_name: string; last_name: string; appointments_count: number
  last_visit_date: string; appointments: Appointment[]
}
export interface Page<T> { items: T[]; total: number }
export interface DayCount { date: string; count: number }
export interface KeyCount { key: string; count: number }
export interface Dashboard {
  today: { total: number; booked: number; done: number; cancelled: number }
  total_appointments: number; total_patients: number; history_count: number
  active_doctors: number; total_doctors: number; last7: DayCount[]
}
export interface Report {
  total: number; done: number; cancelled: number; with_history: number
  per_day: DayCount[]; by_category: KeyCount[]; by_procedure: KeyCount[]; by_doctor: KeyCount[]
}
export interface AdminUser { id: number; name: string }

export type Theme = 'light' | 'dark' | 'auto'
export interface Settings { theme: Theme; texts: Record<string, string> }
