<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import Icon from '../../components/Icon.vue'
import { api } from '../../lib/api'
import { fa, fmtCode, fmtMobile } from '../../lib/fa'
import { addDays, dateToIso, isoJText, timeText, today } from '../../lib/jalali'
import { PROCS, STATUS, STATUS_LIST } from '../../lib/labels'
import type { Appointment, Doctor, Status } from '../../lib/types'
import StatusChip from './StatusChip.vue'

const f = reactive({ q: '', range: 'all', category: '', status: '', doctor_id: '' })
const items = ref<Appointment[]>([]); const total = ref(0)
const doctors = ref<Doctor[]>([])
const open = ref<number | null>(null); const del = ref<number | null>(null)
const loading = ref(false)
let timer = 0

async function load() {
  loading.value = true
  const t = today()
  try {
    const r = await api.appointments({
      q: f.q, category: f.category, status: f.status, doctor_id: f.doctor_id,
      date_from: f.range === 'today' ? dateToIso(t) : f.range === 'week' ? dateToIso(addDays(t, -6)) : '', limit: 150,
    })
    items.value = r.items; total.value = r.total
  } finally { loading.value = false }
}
onMounted(async () => { doctors.value = await api.doctors(); await load() })
watch(() => [f.range, f.category, f.status, f.doctor_id], load)
watch(() => f.q, () => { clearTimeout(timer); timer = window.setTimeout(load, 300) })

async function setStatus(a: Appointment, s: Status) { Object.assign(a, await api.setStatus(a.id, s)) }
async function remove(a: Appointment) { await api.deleteAppointment(a.id); del.value = null; open.value = null; await load() }
const opts = {
  range: [['all', 'همه'], ['today', 'امروز'], ['week', '۷ روز اخیر']],
  category: [['', 'همه'], ['eye', 'چشم'], ['cos', 'زیبایی']],
  status: [['', 'همه وضعیت‌ها'], ...STATUS_LIST.map((s) => [s, STATUS[s]])],
} as const
</script>
<template>
  <div class="box"><div class="filters">
    <input v-model="f.q" class="inp" placeholder="جستجوی نام، موبایل یا کد پذیرش" autocomplete="off" />
    <div v-for="(o, k) in opts" :key="k" class="segs"><button v-for="[v, l] in o" :key="v" type="button" class="seg" :class="{ on: f[k] === v }" @click="f[k] = v">{{ l }}</button></div>
    <select v-model="f.doctor_id" class="inp" aria-label="پزشک"><option value="">همه پزشکان</option><option v-for="d in doctors" :key="d.id" :value="String(d.id)">{{ d.name }}</option></select>
  </div></div>
  <div class="box">
    <div v-if="!items.length && !loading" class="empty">نوبتی با این فیلترها پیدا نشد.</div>
    <template v-else>
      <div class="sub cnt">{{ fa(total) }} نوبت{{ total > items.length ? ` (${fa(items.length)} مورد اول)` : '' }}</div>
      <div v-for="r in items" :key="r.id" class="ap" :class="{ open: open === r.id }">
        <button type="button" class="ap-h" @click="open = open === r.id ? null : r.id; del = null">
          <span class="code">{{ fa(fmtCode(r.code)) }}</span>
          <span class="who"><b>{{ r.first_name }} {{ r.last_name }}</b><small>{{ PROCS[r.procedure].name }} · {{ r.doctor_name }} · {{ isoJText(r.visit_date) }} {{ timeText(r.created_at) }}</small></span>
          <StatusChip :status="r.status" />
        </button>
        <div v-if="open === r.id" class="ap-b">
          <div class="kv"><span>موبایل</span><b dir="ltr">{{ fa(fmtMobile(r.mobile)) }}</b><span>سابقه جراحی</span><b>{{ r.has_history ? 'دارد' : 'ندارد' }}</b><span>شماره نوبت آن روز</span><b>{{ fa(r.seq) }}</b></div>
          <div class="ap-act">
            <div class="segs"><button v-for="s in STATUS_LIST" :key="s" type="button" class="seg" :class="{ on: r.status === s }" @click="setStatus(r, s)">{{ STATUS[s] }}</button></div>
            <span class="grow" />
            <template v-if="del === r.id"><button type="button" class="mini bad" @click="remove(r)">تأیید حذف</button><button type="button" class="mini" @click="del = null">انصراف</button></template>
            <button v-else type="button" class="mini bad" @click="del = r.id"><Icon name="trash" />حذف</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
