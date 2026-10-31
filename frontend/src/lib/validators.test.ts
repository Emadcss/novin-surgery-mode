import { describe, expect, it } from 'vitest'
import { fa, fmtCode, fmtMobile, normDigits } from './fa'
import { dateToIso, isoToDate, jMMDD, jToDate, jp, monthLen } from './jalali'
import { cleanNameInput, mobOk, nameOk } from './validators'

describe('digits', () => {
  it('converts', () => {
    expect(fa(1405)).toBe('۱۴۰۵')
    expect(normDigits('۰۹۱۲-٣٤٥abc')).toBe('0912345')
    expect(fmtCode('10208061007')).toBe('1-02-0806-1-007')
    expect(fmtMobile('09123456789')).toBe('0912 345 6789')
  })
})

describe('validators', () => {
  it('mobile & names', () => {
    expect(mobOk('09123456789')).toBe(true)
    expect(mobOk('08123456789')).toBe(false)
    expect(nameOk('ا')).toBe(false)
    expect(nameOk('علی')).toBe(true)
    expect(cleanNameInput('Ali علي123  رضا')).toBe(' علی رضا')
  })
})

describe('jalali', () => {
  it('maps known dates', () => {
    expect(jp(isoToDate('2026-10-28'))).toEqual({ y: 1405, m: 8, d: 6 })
    expect(jMMDD({ y: 1405, m: 8, d: 6 })).toBe('0806')
  })
  it('month lengths', () => {
    expect(monthLen(1405, 8)).toBe(30)
    expect(monthLen(1405, 1)).toBe(31)
    expect(monthLen(1403, 12)).toBe(30) // سال کبیسه
    expect(monthLen(1404, 12)).toBe(29)
  })
  it('round-trips', () => {
    expect(dateToIso(jToDate(1405, 8, 1))).toBe('2026-10-23')
  })
})
