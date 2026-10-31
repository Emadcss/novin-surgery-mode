<script setup lang="ts">
import { fa } from '../lib/fa'
import Icon from './Icon.vue'
defineEmits<{ key: [k: string] }>()
</script>
<template>
  <div class="numpad" role="group" aria-label="صفحه‌کلید عددی">
    <button v-for="n in 9" :key="n" type="button" class="key" @click="$emit('key', String(n))">{{ fa(n) }}</button>
    <button type="button" class="key fn" @click="$emit('key', 'clear')">پاک‌کردن</button>
    <button type="button" class="key" @click="$emit('key', '0')">{{ fa(0) }}</button>
    <button type="button" class="key fn" aria-label="حذف" @click="$emit('key', 'bk')"><Icon name="bk" /></button>
  </div>
</template>
