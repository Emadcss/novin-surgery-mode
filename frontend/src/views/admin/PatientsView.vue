<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { api } from '../../lib/api'
import { fa, fmtCode, fmtMobile } from '../../lib/fa'
import { isoJText } from '../../lib/jalali'
import { PROCS } from '../../lib/labels'
import type { Patient } from '../../lib/types'
import StatusChip from './StatusChip.vue'

const q = ref(''); const items = ref<Patient[]>([]); const open = ref<string | null>(null)
let timer = 0
const load = async () => { items.value = (await api.patients({ q: q.value, limit: 200 })).items }
onMounted(load)
watch(q, () => { clearTimeout(timer); timer = window.setTimeout(load, 300) })
</script>
<template>
  <div class="box"><div class="filters"><input v-model="q" class="inp" placeholder="جستجوی نام یا شماره موبایل" autocomplete="off" /></div></div>
  <div class="box">
    <div v-if="!items.length" class="empty">بیماری پیدا نشد.</div>
    <template v-else>
      <div class="sub cnt">{{ fa(items.length) }} بیمار</div>
      <div v-for="g in items" :key="g.mobile" class="ap" :class="{ open: open === g.mobile }">
        <button type="button" class="ap-h" @click="open = open === g.mobile ? null : g.mobile">
          <span class="code" style="direction: ltr">{{ fa(fmtMobile(g.mobile)) }}</span>
          <span class="who"><b>{{ g.first_name }} {{ g.last_name }}</b><small>آخرین مراجعه: {{ isoJText(g.last_visit_date) }}</small></span>
          <span class="chip">{{ fa(g.appointments_count) }} پرونده</span>
        </button>
        <div v-if="open === g.mobile" class="ap-b">
          <div v-for="r in g.appointments" :key="r.id" class="row-i"><span class="code">{{ fa(fmtCode(r.code)) }}</span>
            <div style="min-width: 0"><div class="nm">{{ PROCS[r.procedure].name }}</div><div class="sub">{{ r.doctor_name }} · {{ isoJText(r.visit_date) }}</div></div><StatusChip :status="r.status" /></div>
        </div>
      </div>
    </template>
  </div>
</template>
