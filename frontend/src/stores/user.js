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

  const displayName = computed(() => nickname.value || username.value)

  async function login(form) {
    const { data } = await loginApi(form.username, form.password)
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('username', form.username)
    username.value = form.username
    router.push('/')
    loadProfile()
  }

  async function register(form) {
    await registerApi(form.username, form.password)
    await login(form)
  }

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

  async function loadProfile() {
    try {
      const { data } = await getProfile()
      nickname.value = data.nickname || ''
      avatar.value = data.avatar || ''
      if (data.preferences) {
        preferences.value = JSON.parse(data.preferences)
      }
    } catch {
      // ignore
    }
  }

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

  // load profile on init if token exists
  if (token.value) {
    loadProfile()
  }

  return { token, username, nickname, avatar, preferences, displayName, login, register, logout, loadProfile, saveProfile }
})
