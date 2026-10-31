<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import BrandMark from '../../components/BrandMark.vue'
import ClockBox from '../../components/ClockBox.vue'
import Icon from '../../components/Icon.vue'
import ShellFrame from '../../components/ShellFrame.vue'
import { useAuth } from '../../stores/auth'

const NAV = [
  ['dashboard', 'grid', 'داشبورد'], ['appointments', 'cal', 'نوبت‌ها'], ['doctors', 'doc', 'پزشکان'],
  ['patients', 'users', 'بیماران'], ['reports', 'chart', 'گزارش‌ها'], ['admins', 'lock', 'ادمین‌ها'],
] as const
const TITLES: Record<string, string> = { dashboard: 'داشبورد', appointments: 'مدیریت نوبت', doctors: 'مدیریت پزشکان', patients: 'مدیریت بیماران', reports: 'گزارش‌گیری', admins: 'مدیریت ادمین‌ها' }
const route = useRoute(); const router = useRouter(); const auth = useAuth()
const name = computed(() => String(route.name ?? 'dashboard'))
function exit() { auth.logout(); void router.replace('/') }
</script>
<template>
  <ShellFrame mode="admin" screen="admin">
    <div class="adm">
      <nav class="adm-nav">
        <BrandMark />
        <button v-for="[n, ic, l] in NAV" :key="n" type="button" class="nav-i" :class="{ on: name === n }" @click="router.push({ name: n })"><Icon :name="ic" /><span>{{ l }}</span></button>
        <button type="button" class="nav-i exit" @click="exit"><Icon name="exit" /><span>خروج</span></button>
      </nav>
      <main class="adm-main">
        <div class="adm-h"><div><h1>{{ TITLES[name] }}</h1><small v-if="auth.admin" class="sub">{{ auth.admin.name }}</small></div><ClockBox /></div>
        <RouterView />
      </main>
    </div>
  </ShellFrame>
</template>
