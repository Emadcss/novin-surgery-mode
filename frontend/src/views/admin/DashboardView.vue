<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '../../lib/api'
import { dateToIso, dayShort, isoJText, jp, jToDate, monthLen, MONTHS, today, WEEKDAYS, type J } from '../../lib/jalali'
import { fa, fmtCode, pad2 } from '../../lib/fa'
import { PROCS } from '../../lib/labels'
import type { Appointment, Dashboard, DayCount } from '../../lib/types'
import Icon from '../../components/Icon.vue'
import StatusChip from './StatusChip.vue'

const stats = ref<Dashboard | null>(null)
const t = jp(today())
const y = ref(t.y); const m = ref(t.m)
const counts = ref<Record<string, number>>({})
const sel = ref<string>(dateToIso(today()))
const day = ref<Appointment[]>([])

const iso = (j: J) => dateToIso(jToDate(j.y, j.m, j.d))
const off = computed(() => (jToDate(y.value, m.value, 1).getUTCDay() + 1) % 7)
const len = computed(() => monthLen(y.value, m.value))
const todayIso = dateToIso(today())

async function loadMonth() {
  const rows: DayCount[] = await api.calendar(iso({ y: y.value, m: m.value, d: 1 }), iso({ y: y.value, m: m.value, d: len.value }))
  counts.value = Object.fromEntries(rows.map((r) => [r.date, r.count]))
}
async function loadDay() { day.value = (await api.appointments({ date_from: sel.value, date_to: sel.value, limit: 200 })).items }
function shift(n: number) { m.value += n; if (m.value > 12) { m.value = 1; y.value++ } if (m.value < 1) { m.value = 12; y.value-- } }
onMounted(async () => { stats.value = await api.dashboard(); await Promise.all([loadMonth(), loadDay()]) })
watch([y, m], loadMonth)
watch(sel, loadDay)
const max = computed(() => Math.max(1, ...(stats.value?.last7.map((d) => d.count) ?? [1])))
</script>
<template>
  <template v-if="stats">
    <div class="stats">
      <div class="stat"><span>نوبت‌های امروز</span><b>{{ fa(stats.today.total) }}</b><small>{{ fa(stats.today.booked) }} در انتظار · {{ fa(stats.today.done) }} انجام‌شده</small></div>
      <div class="stat"><span>کل پرونده‌ها</span><b>{{ fa(stats.total_appointments) }}</b><small>از ابتدا تا امروز</small></div>
      <div class="stat"><span>بیماران</span><b>{{ fa(stats.total_patients) }}</b><small>{{ fa(stats.history_count) }} پرونده دارای سابقه</small></div>
      <div class="stat"><span>پزشکان فعال</span><b>{{ fa(stats.active_doctors) }}</b><small>از {{ fa(stats.total_doctors) }} پزشک تعریف‌شده</small></div>
    </div>
    <div class="dash">
      <div class="box">
        <div class="cal-h"><button type="button" aria-label="ماه بعد" @click="shift(1)"><Icon name="back" /></button><h2>{{ MONTHS[m - 1] }} {{ fa(y) }}</h2><button type="button" aria-label="ماه قبل" @click="shift(-1)"><Icon name="next" /></button></div>
        <div class="cal">
          <div v-for="w in WEEKDAYS" :key="w" class="w">{{ w }}</div>
          <div v-for="i in off" :key="'o' + i" />
          <button v-for="d in len" :key="d" type="button" class="d"
                  :class="{ has: counts[`${iso({ y, m, d })}`], sel: sel === iso({ y, m, d }), today: todayIso === iso({ y, m, d }) }"
                  @click="sel = iso({ y, m, d })">{{ fa(d) }}<i v-if="counts[iso({ y, m, d })]">{{ fa(counts[iso({ y, m, d })]!) }}</i></button>
        </div>
      </div>
      <div class="stack">
        <div class="box"><h2>{{ sel === todayIso ? 'امروز — ' : '' }}{{ isoJText(sel) }}</h2>
          <div class="rows">
            <div v-for="r in day" :key="r.id" class="row-i"><span class="code">{{ fa(fmtCode(r.code)) }}</span>
              <div style="min-width: 0"><div class="nm">{{ r.first_name }} {{ r.last_name }}</div><div class="sub">{{ PROCS[r.procedure].name }} · {{ r.doctor_name }}</div></div><StatusChip :status="r.status" /></div>
            <div v-if="!day.length" class="empty">برای این روز نوبتی ثبت نشده است.</div>
          </div></div>
        <div class="box"><h2>نوبت‌های ۷ روز اخیر</h2>
          <div class="b7"><div v-for="d in stats.last7" :key="d.date" class="b7c"><b>{{ fa(d.count) }}</b><span class="b7b"><i :style="{ height: Math.max(4, (d.count / max) * 100) + '%' }" /></span><small>{{ dayShort(d.date) }}</small></div></div></div>
      </div>
    </div>
  </template>
  <div v-else class="empty"><div class="spin" /></div>
</template>
