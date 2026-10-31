const FA = '۰۱۲۳۴۵۶۷۸۹'
const AR = '٠١٢٣٤٥٦٧٨٩'

/** ارقام لاتین → فارسی */
export const fa = (v: string | number): string => String(v).replace(/\d/g, (d) => FA[+d]!)

/** ارقام فارسی/عربی → لاتین و حذف هر کاراکتر غیرعددی */
export const normDigits = (v: string): string =>
  String(v)
    .replace(/[۰-۹]/g, (d) => String(FA.indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String(AR.indexOf(d)))
    .replace(/\D/g, '')

export const pad2 = (n: number): string => String(n).padStart(2, '0')

export const fmtMobile = (s: string): string =>
  s.replace(/^(\d{4})(\d{0,3})(\d{0,4}).*$/, (_m, a: string, b: string, c: string) => [a, b, c].filter(Boolean).join(' '))

/** قالب نمایش کد پذیرش: ۱-۰۲-۰۸۰۶-۰-۰۰۷ */
export const fmtCode = (c: string): string => c.replace(/^(\d)(\d{2})(\d{4})(\d)(\d{3})$/, '$1-$2-$3-$4-$5')
