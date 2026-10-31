<script setup lang="ts">
import DoctorAvatar from '../../components/DoctorAvatar.vue'
import { fa } from '../../lib/fa'
import { useKiosk } from '../../stores/kiosk'
const k = useKiosk()
</script>
<template>
  <div v-if="k.doctorsState === 'loading' || k.doctorsState === 'idle'" class="empty"><div class="spin" /></div>
  <div v-else-if="k.doctorsState === 'error'" class="empty">
    دریافت فهرست پزشکان انجام نشد.
    <button type="button" class="btn sec" style="margin-top: 1rem" @click="k.loadDoctors()">تلاش دوباره</button>
  </div>
  <div v-else-if="!k.doctors.length" class="empty">در حال حاضر پزشکی برای این بخش فعال نیست. لطفاً به میز پذیرش مراجعه کنید.</div>
  <div v-else class="cards doc-cards">
    <button v-for="d in k.doctors" :key="d.id" type="button" class="card" :class="{ sel: k.doctorId === d.id }" @click="k.pickDoctor(d.id)">
      <DoctorAvatar :name="d.name" :photo="d.photo_url" />
      <span class="txt"><b>{{ d.name }}</b><small>{{ d.role }}</small><span class="queue">امروز {{ fa(d.today_count) }} نوبت ثبت شده</span></span>
    </button>
  </div>
</template>
