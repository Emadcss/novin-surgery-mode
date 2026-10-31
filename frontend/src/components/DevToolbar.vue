<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShell, type Preview } from '../composables/useShell'
import { useKiosk } from '../stores/kiosk'

const { preview } = useShell()
const kiosk = useKiosk()
const router = useRouter()
const open = ref(false)
const opts: [Preview, string][] = [['auto', 'خودکار'], ['landscape', 'افقی بزرگ'], ['portrait', 'عمودی بزرگ'], ['mobile', 'موبایل']]
</script>
<template>
  <div class="dev">
    <button type="button" @click="open = !open">نمای طراحی</button>
    <div v-if="open" class="dev-menu">
      <b>چیدمان</b>
      <div class="g"><button v-for="[v, l] in opts" :key="v" type="button" :class="{ on: preview === v }" @click="preview = v">{{ l }}</button></div>
      <b>میان‌بر</b>
      <div class="g">
        <button type="button" @click="open = false; router.push('/admin/login')">پنل مدیریت</button>
        <button type="button" @click="open = false; kiosk.reset(); router.push('/')">صفحه‌ی اول</button>
      </div>
    </div>
  </div>
</template>
