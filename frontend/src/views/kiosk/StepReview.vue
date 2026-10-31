<script setup lang="ts">
import Icon from '../../components/Icon.vue'
import { useTexts } from '../../stores/texts'
const tx = useTexts()
</script>
<template>
  <p class="review-note">{{ tx.t('review.note') }}</p>
  <div class="consent"><Icon name="shield" /><span>{{ tx.t('review.consent') }}</span></div>
</template>
