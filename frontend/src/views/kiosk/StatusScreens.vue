<script setup lang="ts">
import DossierFile from '../../components/DossierFile.vue'
import Icon from '../../components/Icon.vue'
import { useKiosk } from '../../stores/kiosk'
defineProps<{ kind: 'saving' | 'fail' }>()
const k = useKiosk()
</script>
<template>
  <main class="flow">
    <DossierFile />
    <section class="panel">
      <div v-if="kind === 'saving'" class="center"><div class="spin" /><h1>در حال ثبت پرونده</h1><p>لطفاً چند لحظه صبر کنید و صفحه را ترک نکنید.</p></div>
      <div v-else class="center">
        <div class="bad-ico"><Icon name="warn" /></div><h1>ثبت پرونده انجام نشد</h1>
        <p>{{ k.error ? k.error + '. ' : '' }}اطلاعات شما حفظ شده است. دوباره تلاش کنید؛ اگر مشکل ادامه داشت، به میز پذیرش مراجعه کنید.</p>
        <div class="p-foot" style="gap: 1rem; justify-content: center">
          <button type="button" class="btn sec" @click="k.backToFlow()">بازگشت</button>
          <button v-if="k.doctorId" type="button" class="btn pri" @click="k.confirm()">تلاش دوباره</button>
        </div>
      </div>
    </section>
  </main>
</template>
