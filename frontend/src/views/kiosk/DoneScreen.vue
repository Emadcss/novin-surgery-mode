<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import DossierFile from '../../components/DossierFile.vue'
import Icon from '../../components/Icon.vue'
import ReceiptSlip from '../../components/ReceiptSlip.vue'
import { config, inTauri } from '../../lib/config'
import { fa, fmtCode } from '../../lib/fa'
import { printReceipt } from '../../lib/print'
import { useKiosk } from '../../stores/kiosk'
import { useTexts } from '../../stores/texts'

const k = useKiosk()
const tx = useTexts()
const left = ref(45)
const printErr = ref('')
let timer = 0
async function doPrint() {
  printErr.value = ''
  try { if (k.record) await printReceipt(k.record) } catch (e) { printErr.value = 'چاپ قبض انجام نشد؛ لطفاً به میز پذیرش مراجعه کنید.'; console.error(e) }
}
onMounted(() => {
  void config
  if (inTauri()) void doPrint()
  timer = window.setInterval(() => { if (--left.value <= 0) k.reset() }, 1000)
})
onBeforeUnmount(() => clearInterval(timer))
</script>
<template>
  <main v-if="k.record" class="flow">
    <DossierFile />
    <section class="panel">
      <div class="done-wrap">
        <div class="codebox">
          <div class="stamp-inline">پذیرش<br />شد</div>
          <span class="eyebrow">{{ tx.t('done.title') }}</span><span class="k">کد پذیرش</span>
          <div class="code">{{ fa(fmtCode(k.record.code)) }}</div>
          <ul class="steps">
            <li><Icon name="check" />{{ tx.t('done.step1') }}</li>
            <li><Icon name="check" />{{ tx.t('done.wait', { name: `${k.record.first_name} ${k.record.last_name}` }) }}</li>
            <li v-if="!k.record.has_history" class="form"><Icon name="check" /><b>{{ tx.t('done.form') }}</b></li>
          </ul>
          <p v-if="printErr" class="msg">{{ printErr }}</p>
          <div style="display: flex; gap: 0.75rem; margin-top: 0.75rem">
            <button v-if="!inTauri() || printErr" type="button" class="btn sec" style="flex: none" @click="doPrint"><Icon name="print" />چاپ قبض</button>
            <button type="button" class="btn pri" style="flex: none" @click="k.reset()">پایان <Icon name="check" /> <span style="opacity: 0.75">({{ fa(left) }})</span></button>
          </div>
        </div>
        <ReceiptSlip :record="k.record" />
      </div>
    </section>
  </main>
</template>
