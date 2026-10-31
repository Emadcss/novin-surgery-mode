<script setup lang="ts">
import { computed } from 'vue'
import { barcodeBars, barcodeWidth } from '../lib/barcode'
import { fa, fmtCode } from '../lib/fa'
import { receiptRows } from '../lib/receipt'
import { receiptFooter } from '../lib/print'
import type { Appointment } from '../lib/types'

const props = defineProps<{ record: Appointment }>()
const rows = computed(() => receiptRows(props.record))
const bars = computed(() => barcodeBars(props.record.code))
const bw = computed(() => barcodeWidth(bars.value))
</script>
<template>
  <div class="slot">
    <div class="slip-clip">
      <div class="slip">
        <h2>نوین دیدگان</h2>
        <div class="c">قبض پذیرش جراحی</div>
        <hr />
        <div class="c">کد پذیرش</div>
        <div class="big">{{ fa(fmtCode(record.code)) }}</div>
        <dl><template v-for="r in rows" :key="r.label"><dt>{{ r.label }}</dt><dd>{{ r.value }}</dd></template></dl>
        <hr />
        <svg class="bc" :viewBox="`0 0 ${bw} 40`" preserveAspectRatio="none" aria-hidden="true"><rect v-for="b in bars" :key="b.x" :x="b.x" y="0" :width="b.w" height="40" /></svg>
                <div class="c" style="margin-top: 0.375rem">{{ receiptFooter(record) }}</div>
      </div>
    </div>
  </div>
</template>
