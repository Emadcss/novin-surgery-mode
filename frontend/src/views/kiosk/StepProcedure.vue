<script setup lang="ts">
import Icon from '../../components/Icon.vue'
import { EYE_PROCS, PROCS } from '../../lib/labels'
import { useKiosk } from '../../stores/kiosk'
import { useTexts } from '../../stores/texts'
const k = useKiosk()
const tx = useTexts()
</script>
<template>
  <div class="choice">
    <button v-for="p in EYE_PROCS" :key="p" type="button" class="card" :class="{ sel: k.proc === p }" @click="k.pickProc(p)">
      <span class="ico"><Icon :name="PROCS[p].icon" /></span><b>{{ PROCS[p].name }}</b><small>{{ tx.t('card.proc.' + p + '.sub') }}</small>
    </button>
  </div>
</template>
