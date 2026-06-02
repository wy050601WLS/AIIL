/**
 * 路由配置模块
 *
 * 定义前端路由表和导航守卫：
 * - 公开路由：登录页、注册页
 * - 需认证路由：对话页、设置页、知识卡片、学习面板、学习资料（meta.auth = true）
 * - 导航守卫：未登录时重定向到登录页，已登录时跳过登录/注册页
 */

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 公开路由（无需登录）
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },

  // 需认证路由（meta.auth = true，未登录自动跳转 /login）
  { path: '/', name: 'Chat', component: () => import('../views/Chat.vue'), meta: { auth: true } },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue'), meta: { auth: true } },
  { path: '/cards', name: 'Cards', component: () => import('../views/Cards.vue'), meta: { auth: true } },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { auth: true } },
  { path: '/resources', name: 'Resources', component: () => import('../views/Resources.vue'), meta: { auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 导航守卫：auth 路由无 Token 时跳转登录页，已登录时跳过登录/注册页
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.auth && !token) return { name: 'Login' }
  if ((to.name === 'Login' || to.name === 'Register') && token) return { name: 'Chat' }
})

export default router
