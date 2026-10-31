export const mobOk = (s: string): boolean => /^09\d{9}$/.test(s)
export const nameOk = (s: string): boolean => s.replace(/[\s‌]/g, '').length >= 2

/** حذف هر چیزی جز حروف فارسی، فاصله و نیم‌فاصله؛ یکسان‌سازی «ي» و «ك» */
export const cleanNameInput = (v: string): string =>
  v
    .replace(/ي/g, 'ی')
    .replace(/ك/g, 'ک')
    .replace(/[^ء-ھۀ-ی\s‌]/g, '')
    .replace(/\s{2,}/g, ' ')
