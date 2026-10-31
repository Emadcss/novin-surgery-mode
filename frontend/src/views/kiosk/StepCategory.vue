<script setup lang="ts">
import Icon from '../../components/Icon.vue'
import { CATS } from '../../lib/labels'
import type { Category } from '../../lib/types'
import { useKiosk } from '../../stores/kiosk'
const k = useKiosk()
</script>
<template>
  <div class="choice">
    <button v-for="(c, id) in CATS" :key="id" type="button" class="card" :class="{ sel: k.cat === id }" @click="k.pickCat(id as Category)">
      <span class="ico"><Icon :name="c.icon" /></span><b>{{ c.name }}</b><small>{{ c.sub }}</small>
    </button>
  </div>
</template>
