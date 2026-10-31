<script setup lang="ts">
import { ref } from 'vue'
import { ApiError } from '../../lib/api'
import type { Theme } from '../../lib/types'
import { useTheme } from '../../stores/theme'

const t = useTheme()
const err = ref('')
const opts: [Theme, string][] = [['light', 'روشن'], ['dark', 'تیره'], ['auto', 'خودکار (طبق تنظیم دستگاه)']]
async function pick(v: Theme) {
  err.value = ''
  try { await t.set(v) } catch (e) { err.value = e instanceof ApiError ? e.message : 'ذخیره انجام نشد' }
}
</script>
<template>
  <div class="box">
    <h2>ظاهر کیوسک</h2>
    <div class="segs"><button v-for="[v, l] in opts" :key="v" type="button" class="seg" :class="{ on: t.theme === v }" @click="pick(v)">{{ l }}</button></div>
    <p class="theme-note">در محیط کلینیک که نور محیط زیاد است، حالت «روشن» توصیه می‌شود و به‌صورت پیش‌فرض فعال است. حالت تیره فقط در صورت انتخاب شما فعال می‌شود و برای همه‌ی کیوسک‌ها اعمال می‌گردد.</p>
    <div class="msg bad">{{ err }}</div>
  </div>
</template>
