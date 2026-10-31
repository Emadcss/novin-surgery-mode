<script setup lang="ts">
import { computed } from 'vue'
import { mediaUrl } from '../lib/config'

const props = defineProps<{ name: string; photo: string | null; cls?: string }>()
const src = computed(() => mediaUrl(props.photo))
const letter = computed(() => props.name.replace('دکتر', '').trim()[0] ?? '؟')
</script>
<template>
  <img v-if="src" :class="['avatar', cls, 'ph']" :src="src" alt="" />
  <span v-else :class="['avatar', cls]">{{ letter }}</span>
</template>
