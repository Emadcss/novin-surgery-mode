import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuth } from './stores/auth'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'kiosk', component: () => import('./views/kiosk/KioskView.vue') },
    { path: '/admin/login', name: 'login', component: () => import('./views/admin/LoginView.vue') },
    {
      path: '/admin', component: () => import('./views/admin/AdminShell.vue'), meta: { auth: true }, redirect: { name: 'dashboard' },
      children: [
        { path: 'dashboard', name: 'dashboard', component: () => import('./views/admin/DashboardView.vue') },
        { path: 'appointments', name: 'appointments', component: () => import('./views/admin/AppointmentsView.vue') },
        { path: 'doctors', name: 'doctors', component: () => import('./views/admin/DoctorsView.vue') },
        { path: 'patients', name: 'patients', component: () => import('./views/admin/PatientsView.vue') },
        { path: 'reports', name: 'reports', component: () => import('./views/admin/ReportsView.vue') },
        { path: 'admins', name: 'admins', component: () => import('./views/admin/AdminsView.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.auth) return true
  const auth = useAuth()
  if (!auth.admin && !(await auth.loadMe())) return { name: 'login' }
  return true
})
