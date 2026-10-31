<script setup lang="ts">
import Icon from '../../components/Icon.vue'
import { useKiosk } from '../../stores/kiosk'
import { useTexts } from '../../stores/texts'
const k = useKiosk()
const tx = useTexts()
</script>
<template>
  <div class="choice">
    <button type="button" class="card" :class="{ sel: k.history === true }" @click="k.pickHistory(true)"><span class="ico"><Icon name="history" /></span><b>{{ tx.t('card.history.yes') }}</b><small>{{ tx.t('card.history.yes.sub') }}</small></button>
    <button type="button" class="card" :class="{ sel: k.history === false }" @click="k.pickHistory(false)"><span class="ico"><Icon name="first" /></span><b>{{ tx.t('card.history.no') }}</b><small>{{ tx.t('card.history.no.sub') }}</small></button>
  </div>
</template>
