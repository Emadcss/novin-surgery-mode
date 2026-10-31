import { onBeforeUnmount, onMounted, ref, type Ref } from 'vue'

/** پس از ۶۰ ثانیه بی‌حرکتی هشدار می‌دهد و بعد از ۱۵ ثانیه‌ی دیگر پرونده را می‌بندد (حریم خصوصی کیوسک). */
export function useIdle(active: Ref<boolean>, onTimeout: () => void, idleAfter = 60, grace = 15) {
  const warn = ref(false)
  const left = ref(grace)
  let idle = 0
  const touch = () => { idle = 0 }
  const keep = () => { idle = 0; warn.value = false; left.value = grace }
  const id = window.setInterval(() => {
    if (!active.value) { idle = 0; warn.value = false; return }
    idle++
    if (!warn.value && idle >= idleAfter) { warn.value = true; left.value = grace }
    else if (warn.value) { left.value--; if (left.value <= 0) { warn.value = false; idle = 0; onTimeout() } }
  }, 1000)
  onMounted(() => { addEventListener('pointerdown', touch, true); addEventListener('keydown', touch, true) })
  onBeforeUnmount(() => { clearInterval(id); removeEventListener('pointerdown', touch, true); removeEventListener('keydown', touch, true) })
  return { warn, left, keep }
}
