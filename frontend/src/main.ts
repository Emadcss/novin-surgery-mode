import '@fontsource/vazirmatn/400.css'
import '@fontsource/vazirmatn/500.css'
import '@fontsource/vazirmatn/600.css'
import '@fontsource/vazirmatn/700.css'
import '@fontsource/vazirmatn/800.css'
import '@fontsource/ibm-plex-sans-arabic/500.css'
import '@fontsource/ibm-plex-sans-arabic/600.css'
import '@fontsource/ibm-plex-sans-arabic/700.css'
import './styles/app.css'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import { setUnauthorizedHandler } from './lib/api'
import { loadConfig } from './lib/config'
import { router } from './router'
import { useAuth } from './stores/auth'

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
  app.mount('#app')
}
void boot()
