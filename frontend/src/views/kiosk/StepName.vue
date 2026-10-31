<script setup lang="ts">
import PersianKeyboard from '../../components/PersianKeyboard.vue'
import { useShell } from '../../composables/useShell'
import { cleanNameInput, nameOk } from '../../lib/validators'
import { useKiosk } from '../../stores/kiosk'
const k = useKiosk()
const { layout } = useShell()

function key(code: string) {
  const f = k.activeName
  const cur = k[f]
  if (code === 'bk') k[f] = cur.slice(0, -1)
  else if (code === 'space') { if (cur && !/\s$/.test(cur)) k[f] = cur + ' ' }
  else if (code === 'zwnj') { if (cur) k[f] = cur + '‌' }
  else if (code.startsWith('ch:') && cur.length < 24) k[f] = cur + code.slice(3)
  else if (code === 'go') {
    if (f === 'first') { if (nameOk(k.first)) k.activeName = 'last' }
    else if (k.stepValid) { k.first = k.first.trim(); k.last = k.last.trim(); k.next() }
  }
}
</script>
<template>
  <div v-if="layout === 'mobile'" class="entry">
    <label class="m-field"><span class="lbl">نام</span>
      <input class="m-in" :value="k.first" lang="fa" dir="rtl" enterkeyhint="next" maxlength="24" autocomplete="off" spellcheck="false" placeholder="مثلاً علی"
             @input="k.first = cleanNameInput(($event.target as HTMLInputElement).value)" @focus="k.activeName = 'first'" /></label>
    <label class="m-field"><span class="lbl">نام خانوادگی</span>
      <input class="m-in" :value="k.last" lang="fa" dir="rtl" enterkeyhint="done" maxlength="24" autocomplete="off" spellcheck="false" placeholder="مثلاً احمدی"
             @input="k.last = cleanNameInput(($event.target as HTMLInputElement).value)" @focus="k.activeName = 'last'" /></label>
  </div>
  <div v-else class="entry">
    <div v-if="layout !== 'portrait'" class="fields">
      <button type="button" class="field" :class="{ cur: k.activeName === 'first', ok: nameOk(k.first) }" @click="k.activeName = 'first'"><span class="lbl">نام</span><span class="txt">{{ k.first }}</span></button>
      <button type="button" class="field" :class="{ cur: k.activeName === 'last', ok: nameOk(k.last) }" @click="k.activeName = 'last'"><span class="lbl">نام خانوادگی</span><span class="txt">{{ k.last }}</span></button>
    </div>
    <PersianKeyboard :go-label="k.activeName === 'last' ? 'تأیید' : 'نام خانوادگی'" @key="key" />
  </div>
</template>
