<script setup lang="ts">
import { computed } from 'vue'
import DossierFile from '../../components/DossierFile.vue'
import Icon from '../../components/Icon.vue'
import { fa } from '../../lib/fa'
import { useKiosk, type StepId } from '../../stores/kiosk'
import { useTexts } from '../../stores/texts'
import StepCategory from './StepCategory.vue'
import StepDoctor from './StepDoctor.vue'
import StepHistory from './StepHistory.vue'
import StepMobile from './StepMobile.vue'
import StepName from './StepName.vue'
import StepProcedure from './StepProcedure.vue'
import StepReview from './StepReview.vue'

const k = useKiosk()
const tx = useTexts()
const comps: Record<StepId, unknown> = { cat: StepCategory, proc: StepProcedure, doctor: StepDoctor, name: StepName, mobile: StepMobile, history: StepHistory, review: StepReview }
const hint = computed(() => tx.t(`step.${k.step}.hint`))
</script>
<template>
  <main class="flow">
    <DossierFile />
    <section class="panel">
      <div class="p-head">
        <div class="p-title">
          <span class="eyebrow">بخش {{ fa(k.position + 1) }} از {{ fa(k.visible.length) }}</span>
          <h1>{{ tx.t(`step.${k.step}.title`) }}</h1>
          <p v-if="hint">{{ hint }}</p>
        </div>
        <button v-if="k.position > 0" type="button" class="back" @click="k.back()"><Icon name="back" />بازگشت</button>
      </div>
      <div class="p-main"><component :is="comps[k.step]" /></div>
      <div v-if="k.step === 'review'" class="p-foot">
        <button type="button" class="btn pri big" @click="k.confirm()"><Icon name="check" />تأیید و صدور کد پذیرش</button>
      </div>
    </section>
  </main>
</template>
