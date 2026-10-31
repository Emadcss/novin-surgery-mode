import './styles/fonts.css'
import './styles/app.css'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import { setUnauthorizedHandler } from './lib/api'
import { loadConfig } from './lib/config'
import { router } from './router'
import { useAuth } from './stores/auth'
import { useTheme } from './stores/theme'

document.documentElement.lang = 'fa'
document.documentElement.dir = 'rtl'

async function boot() {
  await loadConfig()
  const app = createApp(App)
  const pinia = createPinia()
  app.use(pinia).use(router)
  const auth = useAuth()
  auth.restore()
  setUnauthorizedHandler(() => { auth.logout(); void router.replace('/admin/login') })
  void useTheme().load()
  app.mount('#app')
}
void boot()
