import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api, setToken } from '../lib/api'
import type { AdminUser } from '../lib/types'

const KEY = 'novin.admin.token'

export const useAuth = defineStore('auth', () => {
  const admin = ref<AdminUser | null>(null)
  const token = ref<string | null>(null)

  function restore() {
    try { token.value = sessionStorage.getItem(KEY) } catch { token.value = null }
    setToken(token.value)
  }
  async function login(pin: string) {
    const r = await api.login(pin)
    token.value = r.access_token
    admin.value = r.admin
    setToken(token.value)
    try { sessionStorage.setItem(KEY, token.value) } catch { /* ignore */ }
  }
  async function loadMe(): Promise<boolean> {
    if (!token.value) return false
    try { admin.value = await api.me(); return true } catch { logout(); return false }
  }
  function logout() {
    token.value = null
    admin.value = null
    setToken(null)
    try { sessionStorage.removeItem(KEY) } catch { /* ignore */ }
  }
  return { admin, token, restore, login, loadMe, logout }
})
