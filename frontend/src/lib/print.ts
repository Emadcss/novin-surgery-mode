import { invoke } from '@tauri-apps/api/core'
import { inTauri } from './config'
import { renderReceiptPng } from './receipt'
import { useTexts } from '../stores/texts'
import type { Appointment } from './types'

/**
 * در پوسته‌ی Tauri قبض به‌صورت تصویر برای چاپگر حرارتی (ESC/POS) فرستاده می‌شود.
 * در مرورگر عادی از پنجره‌ی چاپ مرورگر استفاده می‌شود (استایل @media print فقط قبض را نشان می‌دهد).
 */
/** متن پایین قبض (قابل ویرایش از پنل مدیریت) */
export const receiptFooter = (ap: Appointment): string => useTexts().t('receipt.footer', { name: `${ap.first_name} ${ap.last_name}` })

export async function printReceipt(ap: Appointment): Promise<void> {
  if (inTauri()) {
    const png = await renderReceiptPng(ap, receiptFooter(ap))
    await invoke('print_receipt', { pngBase64: png })
    return
  }
  window.print()
}
