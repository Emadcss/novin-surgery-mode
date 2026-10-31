import { invoke, isTauri } from '@tauri-apps/api/core'

export interface KioskConfig { apiBase: string; kioskKey: string }

export const config: KioskConfig = {
  apiBase: (import.meta.env.VITE_API_BASE ?? '').replace(/\/$/, ''),
  kioskKey: import.meta.env.VITE_KIOSK_KEY ?? '',
}

export const inTauri = (): boolean => {
  try { return isTauri() } catch { return false }
}

/** در پوسته‌ی Tauri آدرس سرور و کلید کیوسک از فایل kiosk.config.json کنار برنامه خوانده می‌شود. */
export async function loadConfig(): Promise<void> {
  if (!inTauri()) return
  try {
    const c = await invoke<{ api_base: string; kiosk_key: string }>('get_kiosk_config')
    if (c.api_base) config.apiBase = c.api_base.replace(/\/$/, '')
    if (c.kiosk_key) config.kioskKey = c.kiosk_key
  } catch (e) {
    console.warn('خواندن تنظیمات کیوسک ممکن نشد', e)
  }
}

export const mediaUrl = (path: string | null): string | null => (path ? config.apiBase + path : null)
