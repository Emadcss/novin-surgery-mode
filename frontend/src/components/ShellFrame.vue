<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useShell } from '../composables/useShell'

const props = defineProps<{ mode: 'kiosk' | 'admin'; screen: string; step?: string }>()
const { layout, size, framed, mode } = useShell()
onMounted(() => { mode.value = props.mode })
watch(() => props.mode, (m) => { mode.value = m })
</script>
<template>
  <div class="shell" :class="{ framed }" :data-layout="layout" :data-screen="screen" :data-step="step ?? screen"
       :style="{ width: size.w + 'px', height: size.h + 'px' }">
    <slot />
  </div>
</template>
