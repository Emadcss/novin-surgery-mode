<script setup lang="ts">
import PhoneDisplay from '../../components/PhoneDisplay.vue'
import NumPad from '../../components/NumPad.vue'
import { useShell } from '../../composables/useShell'
import { fa, normDigits } from '../../lib/fa'
import { useKiosk } from '../../stores/kiosk'
const k = useKiosk()
const { layout } = useShell()
function key(c: string) {
  if (c === 'bk') k.mobile = k.mobile.slice(0, -1)
  else if (c === 'ok') { if (k.stepValid) k.next() }
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
    <button type="button" class="btn pri" :disabled="!k.stepValid" @click="k.next()">ادامه</button>
  </div>
  <div v-else class="entry num">
    <PhoneDisplay :value="k.mobile" :ok="k.stepValid" :message="msg()" />
    <NumPad :ok-disabled="!k.stepValid" @key="key" />
  </div>
</template>
