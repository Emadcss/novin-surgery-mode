<script setup lang="ts">
import { STATUS } from '../../lib/labels'
import type { Status } from '../../lib/types'
defineProps<{ status: Status }>()
</script>
<template><span class="chip" :class="{ bad: status === 'cancelled', good: status === 'done' }">{{ STATUS[status] }}</span></template>
