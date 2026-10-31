<script setup lang="ts">
import DoctorAvatar from '../../components/DoctorAvatar.vue'
import { useKiosk } from '../../stores/kiosk'
import { useTexts } from '../../stores/texts'
const k = useKiosk()
const tx = useTexts()
</script>
<template>
  <div v-if="k.doctorsState === 'loading' || k.doctorsState === 'idle'" class="empty"><div class="spin" /></div>
  <div v-else-if="k.doctorsState === 'error'" class="empty">
    دریافت فهرست پزشکان انجام نشد.
    <button type="button" class="btn sec" style="margin-top: 1rem" @click="k.loadDoctors()">تلاش دوباره</button>
  </div>
  <div v-else-if="!k.doctors.length" class="empty">{{ tx.t('doctor.empty') }}</div>
  <div v-else class="cards doc-cards">
    <button v-for="d in k.doctors" :key="d.id" type="button" class="card" :class="{ sel: k.doctorId === d.id }" @click="k.pickDoctor(d.id)">
      <DoctorAvatar :name="d.name" :photo="d.photo_url" />
      <span class="txt"><b>{{ d.name }}</b><small>{{ d.role }}</small></span>
    </button>
  </div>
</template>
