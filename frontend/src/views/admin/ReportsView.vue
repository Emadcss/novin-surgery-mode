<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import Icon from '../../components/Icon.vue'
import { api } from '../../lib/api'
import { fa, fmtCode } from '../../lib/fa'
import { dayShort, isoJText, timeText } from '../../lib/jalali'
import { CATS, PROCS, STATUS } from '../../lib/labels'
import type { Category, KeyCount, Procedure, Report } from '../../lib/types'

const days = ref(7)
const r = ref<Report | null>(null)
const copied = ref<'' | 'ok' | 'fail'>('')
const load = async () => { copied.value = ''; r.value = await api.report(days.value) }
onMounted(load); watch(days, load)
const dmax = computed(() => Math.max(1, ...(r.value?.per_day.map((d) => d.count) ?? [1])))
const pct = computed(() => (r.value?.total ? Math.round((r.value.with_history / r.value.total) * 100) : 0))
const catName = (k: string) => CATS[k as Category]?.name ?? k
const procName = (k: string) => PROCS[k as Procedure]?.name ?? k
const bm = (rows: KeyCount[]) => Math.max(1, ...rows.map((x) => x.count))

async function copyCsv() {
  const q = (v: string | number) => '"' + String(v).replace(/"/g, '""') + '"'
  const res = await api.appointments({ limit: 500, date_from: '' })
  const head = 'کد پذیرش,نام,نام خانوادگی,موبایل,نوع عمل,پزشک,تاریخ,ساعت,سابقه,وضعیت'
  const cutoff = days.value ? new Date(Date.now() - days.value * 864e5).toISOString().slice(0, 10) : ''
  const rows = res.items.filter((a) => !cutoff || a.visit_date >= cutoff).map((a) =>
    [a.code, a.first_name, a.last_name, a.mobile, PROCS[a.procedure].name, a.doctor_name, isoJText(a.visit_date), timeText(a.created_at), a.has_history ? 'دارد' : 'ندارد', STATUS[a.status]].map(q).join(','))
  try { await navigator.clipboard.writeText([head, ...rows].join('\n')); copied.value = 'ok' } catch { copied.value = 'fail' }
}
void fmtCode
</script>
<template>
  <div class="adm-bar">
    <div class="segs"><button v-for="[v, l] in [[7, '۷ روز اخیر'], [30, '۳۰ روز اخیر'], [0, 'همه']] as const" :key="v" type="button" class="seg" :class="{ on: days === v }" @click="days = v">{{ l }}</button></div>
    <button type="button" class="mini" @click="copyCsv"><Icon name="copy" />کپی گزارش (CSV)</button>
  </div>
  <div v-if="copied" class="demo" style="background: var(--accent-soft); color: var(--accent)">{{ copied === 'fail' ? 'کپی انجام نشد. مرورگر اجازه‌ی دسترسی به کلیپ‌بورد را نداد.' : 'گزارش در کلیپ‌بورد کپی شد.' }}</div>
  <template v-if="r">
    <div class="stats">
      <div class="stat"><span>نوبت ثبت‌شده</span><b>{{ fa(r.total) }}</b></div>
      <div class="stat"><span>انجام‌شده</span><b>{{ fa(r.done) }}</b></div>
      <div class="stat"><span>لغوشده</span><b>{{ fa(r.cancelled) }}</b></div>
      <div class="stat"><span>دارای سابقه</span><b>{{ fa(pct) }}٪</b></div>
    </div>
    <div class="box"><h2>نوبت‌ها به تفکیک روز</h2>
      <div class="b7 long"><div v-for="d in r.per_day" :key="d.date" class="b7c"><b>{{ d.count ? fa(d.count) : '' }}</b><span class="b7b"><i :style="{ height: d.count ? Math.max(6, (d.count / dmax) * 100) + '%' : '0' }" /></span><small>{{ dayShort(d.date) }}</small></div></div></div>
    <div class="dash">
      <div class="box">
        <h2>به تفکیک نوع جراحی</h2>
        <div v-for="x in r.by_category" :key="x.key" class="hbar"><span>{{ catName(x.key) }}</span><span class="tr"><i :style="{ width: (x.count / bm(r.by_category)) * 100 + '%' }" /></span><b>{{ fa(x.count) }}</b></div>
        <h2 style="margin-top: 0.5rem">به تفکیک نوع عمل</h2>
        <div v-for="x in r.by_procedure" :key="x.key" class="hbar"><span>{{ procName(x.key) }}</span><span class="tr"><i :style="{ width: (x.count / bm(r.by_procedure)) * 100 + '%' }" /></span><b>{{ fa(x.count) }}</b></div>
        <div v-if="!r.by_procedure.length" class="empty">داده‌ای نیست.</div>
      </div>
      <div class="box"><h2>به تفکیک پزشک</h2>
        <div v-for="x in r.by_doctor" :key="x.key" class="hbar"><span>{{ x.key }}</span><span class="tr"><i :style="{ width: (x.count / bm(r.by_doctor)) * 100 + '%' }" /></span><b>{{ fa(x.count) }}</b></div>
        <div v-if="!r.by_doctor.length" class="empty">داده‌ای نیست.</div></div>
    </div>
  </template>
</template>
