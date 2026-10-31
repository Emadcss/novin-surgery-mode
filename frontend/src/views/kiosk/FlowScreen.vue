<script setup lang="ts">
import { computed } from 'vue'
import DossierFile from '../../components/DossierFile.vue'
import Icon from '../../components/Icon.vue'
import { fa } from '../../lib/fa'
import { STEPS, useKiosk, type StepId } from '../../stores/kiosk'
import StepCategory from './StepCategory.vue'
import StepDoctor from './StepDoctor.vue'
import StepHistory from './StepHistory.vue'
import StepMobile from './StepMobile.vue'
import StepName from './StepName.vue'
import StepProcedure from './StepProcedure.vue'
import StepReview from './StepReview.vue'

const k = useKiosk()
const comps: Record<StepId, unknown> = { cat: StepCategory, proc: StepProcedure, doctor: StepDoctor, name: StepName, mobile: StepMobile, history: StepHistory, review: StepReview }
const st = computed(() => STEPS.find((s) => s.id === k.step)!)
const hint = computed(() => (k.step === 'name' ? st.value.hint : st.value.hint))
</script>
<template>
  <main class="flow">
    <DossierFile />
    <section class="panel">
      <div class="p-head">
        <span class="eyebrow">بخش {{ fa(k.position + 1) }} از {{ fa(k.visible.length) }}</span>
        <h1>{{ st.title }}</h1>
        <p v-if="hint">{{ hint }}</p>
      </div>
      <div class="p-main"><component :is="comps[k.step]" /></div>
      <div class="p-foot">
        <button v-if="k.position > 0" type="button" class="btn sec" @click="k.back()"><Icon name="back" />قبلی</button><span v-else />
        <button v-if="k.step === 'review'" type="button" class="btn pri big" @click="k.confirm()"><Icon name="check" />تأیید و صدور کد پذیرش</button>
        <button v-else type="button" class="btn pri" :disabled="!k.stepValid" @click="k.next()">ادامه <Icon name="next" /></button>
      </div>
    </section>
  </main>
</template>
