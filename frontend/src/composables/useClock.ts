import { onBeforeUnmount, ref } from 'vue'
import { jText, jp, timeText, today } from '../lib/jalali'

export function useClock() {
  const time = ref(timeText())
  const date = ref(jText(jp(today())))
  const id = window.setInterval(() => { time.value = timeText(); date.value = jText(jp(today())) }, 15000)
  onBeforeUnmount(() => clearInterval(id))
  return { time, date }
}
