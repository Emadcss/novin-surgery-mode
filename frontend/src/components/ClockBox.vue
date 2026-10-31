<script setup lang="ts">
import { useClock } from '../composables/useClock'
const { time, date } = useClock()
</script>
<template>
  <div class="clock"><span>{{ time }}</span><small>{{ date }}</small></div>
</template>
