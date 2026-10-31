<script setup lang="ts">
import { fa } from '../lib/fa'
defineProps<{ value: string; len: number; groups: number[] }>()
</script>
<template>
  <div class="comb" aria-live="polite">
    <span v-for="i in len" :key="i" class="cell" :class="{ on: value[i - 1], cur: i - 1 === value.length, gap: groups.includes(i - 1) }">{{ value[i - 1] ? fa(value[i - 1]!) : '' }}</span>
  </div>
</template>
