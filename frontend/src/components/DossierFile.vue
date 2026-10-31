<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { useShell } from '../composables/useShell'
import { fa, fmtCode } from '../lib/fa'
import { jp, today } from '../lib/jalali'
import { LINES, useKiosk } from '../stores/kiosk'

const props = defineProps<{ demo?: boolean }>()
const kiosk = useKiosk()
const { layout } = useShell()
const list = ref<HTMLElement | null>(null)
const widths = [78, 62, 70, 55, 66, 48]
const year = fa(jp(today()).y)

const active = (l: (typeof LINES)[number]) =>
  !props.demo && kiosk.screen === 'flow' &&
  (l.step === kiosk.step || (l.f === 'proc' && kiosk.step === 'cat')) &&
  (l.step !== 'name' || l.f === kiosk.activeName)

const nameLive = (l: (typeof LINES)[number]) => kiosk.screen === 'flow' && kiosk.step === 'name' && l.step === 'name' && layout.value !== 'mobile'
function tap(l: (typeof LINES)[number]) {
  if (nameLive(l)) kiosk.activeName = l.f === 'last' ? 'last' : 'first'
  else kiosk.edit(l.step, l.f)
}

// در حالت موبایل چیپ فعال را وسط نوار می‌آورد
watch(() => [kiosk.step, kiosk.activeName], async () => {
  if (layout.value !== 'mobile' || !list.value || kiosk.step === 'review') return
  await nextTick()
  const el = list.value.querySelector<HTMLElement>('.line.active')
  if (!el) return
  const cr = list.value.getBoundingClientRect(), er = el.getBoundingClientRect()
  list.value.scrollLeft += er.left + er.width / 2 - (cr.left + cr.width / 2)
})
</script>
<template>
  <aside class="file" aria-label="پرونده بیمار">
    <div class="file-tab">پرونده جدید</div>
    <div class="file-body">
      <div class="file-sheet">
        <svg class="clip" viewBox="0 0 24 60" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M17 20v28a7 7 0 01-14 0V12a5 5 0 0110 0v32a3 3 0 01-6 0V20" /></svg>
        <div class="file-head">
          <span class="file-title">پرونده بیمار</span>
          <span class="file-no">{{ kiosk.record ? fa(fmtCode(kiosk.record.code)) : demo ? '—' : 'در حال تشکیل' }}</span>
        </div>
        <ul ref="list" class="lines">
          <li v-for="(l, i) in LINES" :key="l.f">
            <div v-if="demo" class="line"><span class="lbl">{{ l.lbl }}</span><span class="val" :style="{ '--w': widths[i] + '%' }" /></div>
            <button v-else type="button" class="line" :data-step="l.step" :class="{ done: kiosk.fieldDone(l.f), active: active(l), edit: kiosk.canEdit(l) }"
                    :disabled="!nameLive(l) && !kiosk.canEdit(l)" :tabindex="nameLive(l) || kiosk.canEdit(l) ? 0 : -1" @click="tap(l)">
              <span class="lbl">{{ l.lbl }}</span>
              <span :key="kiosk.fieldText(l.f)" class="val">{{ kiosk.fieldText(l.f) }}</span>
            </button>
          </li>
        </ul>
        <div class="file-foot">
          <span>{{ fa(kiosk.doneCount) }} از {{ fa(LINES.length) }} بخش تکمیل شد</span>
          <span class="bar-track"><span class="bar-fill" :style="{ width: (kiosk.doneCount / LINES.length) * 100 + '%' }" /></span>
        </div>
        <div class="seal" :class="{ on: kiosk.screen === 'done' }">پذیرش شد<small>{{ year }}</small></div>
      </div>
    </div>
  </aside>
</template>
