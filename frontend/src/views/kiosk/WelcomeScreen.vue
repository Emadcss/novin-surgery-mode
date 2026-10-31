<script setup lang="ts">
import DossierFile from '../../components/DossierFile.vue'
import Icon from '../../components/Icon.vue'
import { useKiosk } from '../../stores/kiosk'
const k = useKiosk()
</script>
<template>
  <main class="welcome">
    <div class="w-copy">
      <div class="w-text">
        <p class="eyebrow">پذیرش خودکار جراحی</p>
        <h1>پرونده جراحی خود را <em>همین‌جا</em> بسازید</h1>
        <p>در چند مرحله کوتاه، نوع عمل و پزشک را انتخاب کنید، مشخصات‌تان را وارد کنید و کد پذیرش و قبض را همراه ببرید.</p>
      </div>
      <button class="cta" type="button" @click="k.start()">شروع پذیرش <Icon name="next" /></button>
      <ul class="w-points"><li><Icon name="clock" />حدود ۲ دقیقه</li><li><Icon name="shield" />اطلاعات شما محرمانه می‌ماند</li></ul>
    </div>
    <div class="w-art"><DossierFile demo /></div>
  </main>
</template>
