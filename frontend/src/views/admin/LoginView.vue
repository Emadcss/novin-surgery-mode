<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BrandMark from '../../components/BrandMark.vue'
import Icon from '../../components/Icon.vue'
import NumPad from '../../components/NumPad.vue'
import ShellFrame from '../../components/ShellFrame.vue'
import { ApiError } from '../../lib/api'
import { useAuth } from '../../stores/auth'

const auth = useAuth()
const router = useRouter()
const pin = ref('')
const bad = ref('')
const busy = ref(false)
const shake = ref(false)

async function key(k: string) {
  if (busy.value) return
  bad.value = ''
  if (k === 'bk') pin.value = pin.value.slice(0, -1)
  else if (k === 'clear') pin.value = ''
  else if (/^\d$/.test(k) && pin.value.length < 4) pin.value += k
  if (pin.value.length === 4) {
    busy.value = true
    try { await auth.login(pin.value); await router.replace('/admin') }
    catch (e) {
      bad.value = e instanceof ApiError ? e.message : 'خطا'
      shake.value = true; setTimeout(() => (shake.value = false), 500)
    } finally { pin.value = ''; busy.value = false }
  }
}
</script>
<template>
  <ShellFrame mode="admin" screen="login">
    <header class="bar"><BrandMark /><div class="grow" /><button class="ghost" type="button" @click="router.push('/')"><Icon name="back" />بازگشت به کیوسک</button></header>
    <main class="login">
      <div class="box" :class="{ shake }">
        <span class="eyebrow">پنل مدیریت</span>
        <h2 style="font-size: var(--fs-lg)">رمز ورود را وارد کنید</h2>
        <div class="pin"><i v-for="i in 4" :key="i" :class="{ on: i <= pin.length }" /></div>
        <div class="msg" :class="{ bad }">{{ bad }}</div>
        <div style="max-width: 20rem; width: 100%"><NumPad @key="key" /></div>
      </div>
    </main>
  </ShellFrame>
</template>
