<script setup lang="ts">
import { RouterView } from 'vue-router'
import DevToolbar from './components/DevToolbar.vue'
const dev = import.meta.env.DEV
</script>
<template>
  <RouterView />
  <DevToolbar v-if="dev" />
</template>
