<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const emit = defineEmits<{ close: [] }>()
const dlg = ref<HTMLElement | null>(null)
let prev: HTMLElement | null = null
const FOCUSABLE = 'button:not([disabled]),input:not([disabled]),select:not([disabled]),[href],[tabindex]:not([tabindex="-1"])'

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') { e.stopPropagation(); emit('close'); return }
  if (e.key !== 'Tab' || !dlg.value) return
  const items = [...dlg.value.querySelectorAll<HTMLElement>(FOCUSABLE)].filter((x) => x.offsetParent !== null)
  if (!items.length) { e.preventDefault(); return }
  const first = items[0]!, last = items[items.length - 1]!
  if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
}
onMounted(() => {
  prev = document.activeElement as HTMLElement | null
  const first = dlg.value?.querySelector<HTMLElement>('input,select,button:not(.mini)') ?? dlg.value
  first?.focus({ preventScroll: true })
})
onBeforeUnmount(() => prev?.focus?.({ preventScroll: true }))
</script>
<template>
  <div class="modal" @keydown="onKey"><div ref="dlg" class="dialog" role="dialog" aria-modal="true" tabindex="-1"><slot /></div></div>
</template>
