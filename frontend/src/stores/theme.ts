import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../lib/api'
import type { Theme } from '../lib/types'

const mq = typeof matchMedia === 'function' ? matchMedia('(prefers-color-scheme: dark)') : null

/** تم کیوسک را ادمین از پنل مدیریت تعیین می‌کند؛ پیش‌فرض (و در صورت خطای شبکه) روشن است. */
export const useTheme = defineStore('theme', () => {
  const theme = ref<Theme>('light')

  function apply() {
    const dark = theme.value === 'dark' || (theme.value === 'auto' && !!mq?.matches)
    document.documentElement.dataset.theme = dark ? 'dark' : 'light'
  }
  mq?.addEventListener('change', () => { if (theme.value === 'auto') apply() })

  async function load() {
    try { theme.value = (await api.kioskSettings()).theme } catch { theme.value = 'light' }
    apply()
  }
  async function set(t: Theme) {
    theme.value = (await api.setTheme(t)).theme
    apply()
  }
  apply()
  return { theme, load, set }
})
