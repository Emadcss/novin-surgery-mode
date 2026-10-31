import { defineStore } from 'pinia'
import { ref } from 'vue'
import { TEXT_DEFAULTS } from '../lib/texts'

/** متن‌های کیوسک: مقدار ویرایش‌شده‌ی ادمین، وگرنه پیش‌فرض داخل برنامه. */
export const useTexts = defineStore('texts', () => {
  const over = ref<Record<string, string>>({})
  function set(v: Record<string, string> | undefined) { over.value = { ...(v ?? {}) } }
  function t(key: string, vars: Record<string, string> = {}): string {
    const raw = over.value[key] ?? TEXT_DEFAULTS[key] ?? ''
    return raw.replace(/\{(\w+)\}/g, (_, k: string) => vars[k] ?? '')
  }
  return { over, set, t }
})
