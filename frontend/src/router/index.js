import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
  { path: '/', name: 'Chat', component: () => import('../views/Chat.vue'), meta: { auth: true } },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue'), meta: { auth: true } },
  { path: '/cards', name: 'Cards', component: () => import('../views/Cards.vue'), meta: { auth: true } },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.auth && !token) return { name: 'Login' }
  if ((to.name === 'Login' || to.name === 'Register') && token) return { name: 'Chat' }
})

export default router
