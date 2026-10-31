<script setup lang="ts">
import Icon from '../../components/Icon.vue'
import { useKiosk } from '../../stores/kiosk'
const k = useKiosk()
</script>
<template>
  <div class="choice">
    <button type="button" class="card" :class="{ sel: k.history === true }" @click="k.pickHistory(true)"><span class="ico"><Icon name="history" /></span><b>بله، قبلاً عمل کرده‌ام</b><small>در این مرکز پرونده دارم</small></button>
    <button type="button" class="card" :class="{ sel: k.history === false }" @click="k.pickHistory(false)"><span class="ico"><Icon name="first" /></span><b>خیر، اولین بار است</b><small>پرونده جدید ایجاد می‌شود</small></button>
  </div>
</template>
