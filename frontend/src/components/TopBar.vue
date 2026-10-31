<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BrandMark from './BrandMark.vue'
import ClockBox from './ClockBox.vue'
import Icon from './Icon.vue'

defineProps<{ cancel?: boolean }>()
const emit = defineEmits<{ cancel: [] }>()

/** پنج لمس پشت‌سرهم روی لوگو، ورود به پنل مدیریت را باز می‌کند (برای بیمار دیده نمی‌شود). */
const router = useRouter()
const taps = ref<number[]>([])
function tapLogo() {
  const now = Date.now()
  taps.value = [...taps.value.filter((t) => now - t < 3000), now]
  if (taps.value.length >= 5) { taps.value = []; void router.push('/admin/login') }
}
</script>
<template>
  <header class="bar">
    <div @click="tapLogo"><BrandMark /></div>
    <div class="grow" />
    <ClockBox />
    <button v-if="cancel" class="ghost" type="button" @click="emit('cancel')"><Icon name="x" />انصراف</button>
  </header>
</template>
