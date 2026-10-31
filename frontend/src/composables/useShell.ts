import { computed, reactive, ref, watchEffect } from 'vue'

export type Layout = 'landscape' | 'portrait' | 'mobile'
export type Preview = 'auto' | Layout

/** ابعاد مرجع طراحی هر چیدمان (px). 1rem = 16px در همین ابعاد. */
export const REF: Record<Layout, [number, number]> = { landscape: [1280, 800], portrait: [800, 1280], mobile: [390, 844] }

const preview = ref<Preview>('auto')
const mode = ref<'kiosk' | 'admin'>('kiosk')
const win = reactive({ w: window.innerWidth, h: window.innerHeight })
window.addEventListener('resize', () => { win.w = window.innerWidth; win.h = window.innerHeight })

const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v))

const layout = computed<Layout>(() => {
  if (preview.value !== 'auto') return preview.value
  return win.w <= 640 ? 'mobile' : win.w >= win.h ? 'landscape' : 'portrait'
})

const size = computed(() => {
  if (preview.value === 'auto') return { w: win.w, h: win.h }
  const [rw, rh] = REF[layout.value]
  const k = Math.min((win.w - 24) / rw, (win.h - 24) / rh, 1.7)
  return { w: Math.round(rw * k), h: Math.round(rh * k) }
})

/** ضریب مقیاس: کیوسک کل پنل را پر می‌کند؛ پنل ادمین روی مانیتورهای بزرگ بیش از حد درشت نمی‌شود. */
const unit = computed(() => {
  const [rw, rh] = REF[layout.value]
  const { w, h } = size.value
  if (layout.value === 'mobile') return clamp(w / rw, 0.85, mode.value === 'admin' ? 1.3 : 1.5)
  const u = Math.min(w / rw, h / rh)
  return mode.value === 'admin' ? clamp(u, 0.8, 1.15) : u
})

watchEffect(() => { document.documentElement.style.fontSize = `${(16 * unit.value).toFixed(3)}px` })

export function useShell() {
  return { preview, mode, layout, size, unit, framed: computed(() => preview.value !== 'auto') }
}
