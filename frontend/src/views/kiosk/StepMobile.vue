<script setup lang="ts">
import CombDisplay from '../../components/CombDisplay.vue'
import NumPad from '../../components/NumPad.vue'
import { useShell } from '../../composables/useShell'
import { fa, normDigits } from '../../lib/fa'
import { useKiosk } from '../../stores/kiosk'
const k = useKiosk()
const { layout } = useShell()
function key(c: string) {
  if (c === 'bk') k.mobile = k.mobile.slice(0, -1)
  else if (c === 'clear') k.mobile = ''
  else if (/^\d$/.test(c) && k.mobile.length < 11) k.mobile += c
}
const msg = () => (k.mobile.length >= 2 && !k.mobile.startsWith('09') ? 'شماره موبایل باید با ۰۹ شروع شود' : '')
</script>
<template>
  <div v-if="layout === 'mobile'" class="entry">
    <label class="m-field"><span class="lbl">شماره موبایل</span>
      <input class="m-in" :value="fa(k.mobile)" inputmode="tel" maxlength="11" dir="ltr" enterkeyhint="next" autocomplete="off" placeholder="۰۹۱۲۰۰۰۰۰۰۰"
             @input="k.mobile = normDigits(($event.target as HTMLInputElement).value).replace(/\D/g, '').slice(0, 11)" /></label>
    <div class="msg">{{ msg() }}</div>
  </div>
  <div v-else class="entry num">
    <div class="disp"><CombDisplay :value="k.mobile" :len="11" :groups="[3, 6]" /><div class="msg">{{ msg() }}</div></div>
    <NumPad @key="key" />
  </div>
</template>
