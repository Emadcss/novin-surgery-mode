/** میله‌های تزئینی بارکد از روی رقم‌های کد (برای قبض) */
export function barcodeBars(code: string): { x: number; w: number }[] {
  const bars: { x: number; w: number }[] = []
  let x = 0
  for (const ch of code + [...code].reverse().join('')) {
    const n = +ch
    const w = 1 + (n % 3)
    bars.push({ x, w })
    x += w + 1 + (n % 2)
  }
  return bars
}
export const barcodeWidth = (bars: { x: number; w: number }[]): number => {
  const last = bars[bars.length - 1]
  return last ? last.x + last.w : 0
}
