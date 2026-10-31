<script setup lang="ts">
import { computed } from 'vue'
import ModalDialog from '../../components/ModalDialog.vue'
import ShellFrame from '../../components/ShellFrame.vue'
import TopBar from '../../components/TopBar.vue'
import { useIdle } from '../../composables/useIdle'
import { useKiosk } from '../../stores/kiosk'
import { ref } from 'vue'
import DoneScreen from './DoneScreen.vue'
import FlowScreen from './FlowScreen.vue'
import StatusScreens from './StatusScreens.vue'
import WelcomeScreen from './WelcomeScreen.vue'

const k = useKiosk()
const cancelOpen = ref(false)
const active = computed(() => k.screen !== 'welcome' && k.screen !== 'saving')
const idle = useIdle(active, () => { cancelOpen.value = false; k.reset() })
const showCancel = computed(() => k.screen === 'flow')
function yes() { cancelOpen.value = false; k.reset() }
</script>
<template>
  <ShellFrame mode="kiosk" :screen="k.screen" :step="k.screen === 'flow' ? k.step : k.screen">
    <TopBar :cancel="showCancel" @cancel="cancelOpen = true" />
    <WelcomeScreen v-if="k.screen === 'welcome'" />
    <FlowScreen v-else-if="k.screen === 'flow'" />
    <StatusScreens v-else-if="k.screen === 'saving' || k.screen === 'fail'" :kind="k.screen" />
    <DoneScreen v-else-if="k.screen === 'done'" />
    <ModalDialog v-if="cancelOpen" @close="cancelOpen = false">
      <h2>پذیرش لغو شود؟</h2><p>اطلاعات واردشده پاک می‌شود و به صفحه‌ی اول برمی‌گردید.</p>
      <div class="row"><button type="button" class="btn sec" @click="cancelOpen = false">ادامه می‌دهم</button><button type="button" class="btn warn" @click="yes">لغو پذیرش</button></div>
    </ModalDialog>
    <ModalDialog v-else-if="idle.warn.value" @close="idle.keep()">
      <h2>هنوز اینجا هستید؟</h2><p>برای حفظ حریم خصوصی، پس از <span class="count">{{ idle.left.value }}</span> ثانیه پرونده بسته می‌شود.</p>
      <div class="row"><button type="button" class="btn pri" style="max-width: none" @click="idle.keep()">بله، ادامه می‌دهم</button></div>
    </ModalDialog>
  </ShellFrame>
</template>
