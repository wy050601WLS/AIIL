/**
 * 用户状态管理 Store
 *
 * 管理用户认证状态（token/用户名）和个人资料（昵称/头像/偏好）。
 * 登录后自动加载个人资料，Token 持久化到 localStorage。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getProfile, updateProfile as updateProfileApi } from '../api/auth'
import router from '../router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const nickname = ref('')
  const avatar = ref('')
  const preferences = ref(null)

  /** 显示名称：优先显示昵称，否则显示用户名 */
  const displayName = computed(() => nickname.value || username.value)

  /** 用户登录：保存 Token → 跳转首页 → 异步加载资料 */
  async function login(form) {
    const { data } = await loginApi(form.username, form.password)
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('username', form.username)
    username.value = form.username
    router.push('/')
    loadProfile()
  }

  /** 用户注册：注册成功后自动登录 */
  async function register(form) {
    await registerApi(form.username, form.password)
    await login(form)
  }

  /** 退出登录：清除所有状态和 localStorage，跳转登录页 */
  function logout() {
    token.value = ''
    username.value = ''
    nickname.value = ''
    avatar.value = ''
    preferences.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    router.push('/login')
  }

  /** 从后端加载用户个人资料（昵称、头像、偏好设置） */
  async function loadProfile() {
    try {
      const { data } = await getProfile()
      nickname.value = data.nickname || ''
      avatar.value = data.avatar || ''
      if (data.preferences) {
        preferences.value = JSON.parse(data.preferences)
      }
    } catch {
      // 加载失败静默处理（Token 可能已过期）
    }
  }

  /** 保存个人资料到后端，偏好设置序列化为 JSON 字符串 */
  async function saveProfile(updates) {
    const payload = {}
    if (updates.nickname !== undefined) payload.nickname = updates.nickname
    if (updates.avatar !== undefined) payload.avatar = updates.avatar
    if (updates.preferences !== undefined) payload.preferences = JSON.stringify(updates.preferences)
    const { data } = await updateProfileApi(payload)
    nickname.value = data.nickname || ''
    avatar.value = data.avatar || ''
    if (data.preferences) {
      preferences.value = JSON.parse(data.preferences)
    }
  }

  // 初始化：如果有 Token 则自动加载用户资料
  if (token.value) {
    loadProfile()
  }

  return { token, username, nickname, avatar, preferences, displayName, login, register, logout, loadProfile, saveProfile }
})
