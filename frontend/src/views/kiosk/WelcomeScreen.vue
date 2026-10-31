<script setup lang="ts">
import DossierFile from '../../components/DossierFile.vue'
import Icon from '../../components/Icon.vue'
import { useKiosk } from '../../stores/kiosk'
import { useTexts } from '../../stores/texts'
const k = useKiosk()
const tx = useTexts()
</script>
<template>
  <main class="welcome">
    <div class="w-copy">
      <div class="w-text">
        <p class="eyebrow">{{ tx.t('welcome.eyebrow') }}</p>
        <h1>پرونده جراحی خود را <em>همین‌جا</em> بسازید</h1>
        <p>{{ tx.t('welcome.body') }}</p>
      </div>
      <button class="cta" type="button" @click="k.start()">شروع پذیرش <Icon name="next" /></button>
      <ul class="w-points"><li><Icon name="clock" />{{ tx.t('welcome.p1') }}</li><li><Icon name="shield" />{{ tx.t('welcome.p2') }}</li></ul>
    </div>
    <div class="w-art"><DossierFile demo /></div>
  </main>
</template>
