/**
 * بررسی زمان کامپایل: تایپ‌های دستی فرانت باید با اسکیمای تولیدشده از FastAPI یکی باشند.
 * اگر بک‌اند فیلدی را عوض کند، `npm run gen:api` و سپس `npm run typecheck` همین‌جا خطا می‌دهد.
 */
import type { components } from './api-schema'
import type { Appointment, AppointmentIn, Doctor, DoctorIn, KioskDoctor, Settings, Theme } from './types'

type S = components['schemas']
type Same<A, B> = [A] extends [B] ? ([B] extends [A] ? true : false) : false
const ok = <_T extends true>() => undefined

ok<Same<keyof Appointment, keyof S['AppointmentOut']>>()
ok<Same<keyof AppointmentIn, keyof S['AppointmentIn']>>()
ok<Same<keyof Doctor, keyof S['DoctorOut']>>()
ok<Same<keyof DoctorIn, keyof S['DoctorIn']>>()
ok<Same<keyof KioskDoctor, keyof S['KioskDoctor']>>()
ok<Same<Theme, S['SettingsOut']['theme']>>()
ok<Same<keyof Settings, keyof S['SettingsOut']>>()
ok<Same<Appointment['procedure'], S['AppointmentOut']['procedure']>>()
ok<Same<Appointment['status'], S['AppointmentOut']['status']>>()
