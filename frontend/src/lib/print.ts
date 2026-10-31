import { invoke } from '@tauri-apps/api/core'
import { inTauri } from './config'
import { renderReceiptPng } from './receipt'
import type { Appointment } from './types'

/**
 * در پوسته‌ی Tauri قبض به‌صورت تصویر برای چاپگر حرارتی (ESC/POS) فرستاده می‌شود.
 * در مرورگر عادی از پنجره‌ی چاپ مرورگر استفاده می‌شود (استایل @media print فقط قبض را نشان می‌دهد).
 */
export async function printReceipt(ap: Appointment): Promise<void> {
  if (inTauri()) {
    const png = await renderReceiptPng(ap)
    await invoke('print_receipt', { pngBase64: png })
    return
  }
  window.print()
}
