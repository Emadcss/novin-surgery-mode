<script setup lang="ts">
import { computed } from 'vue'
import { fa } from '../lib/fa'
import Icon from './Icon.vue'

/** نمایش شماره‌ی موبایل به‌صورت یک کارت بزرگ ۴-۳-۴؛ جای رقم‌های خالی کمرنگ نشان داده می‌شود. */
const props = defineProps<{ value: string; ok: boolean; message?: string }>()
const groups = [4, 3, 4]
const slots = computed(() => {
  let i = 0
  return groups.map((n) => Array.from({ length: n }, () => { const idx = i++; return { ch: props.value[idx] ?? '', cur: idx === props.value.length } }))
})
</script>
<template>
  <div class="phone" :class="{ ok }" aria-live="polite">
    <span class="p-lbl">شماره موبایل<Icon v-if="ok" name="check" /></span>
    <div class="p-digits" dir="ltr">
      <span v-for="(g, gi) in slots" :key="gi" class="p-grp">
        <span v-for="(s, si) in g" :key="si" class="p-d" :class="{ on: s.ch, cur: s.cur }">{{ s.ch ? fa(s.ch) : '' }}</span>
      </span>
    </div>
    <span class="p-msg" :class="{ bad: message }">{{ message || ' ' }}</span>
  </div>
</template>
