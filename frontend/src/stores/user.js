import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, register as registerApi } from '../api/auth'
import router from '../router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')

  async function login(form) {
    const { data } = await loginApi(form.username, form.password)
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('username', form.username)
    username.value = form.username
    router.push('/')
  }

  async function register(form) {
    await registerApi(form.username, form.password)
    await login(form)
  }

  function logout() {
    token.value = ''
    username.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    router.push('/login')
  }

  return { token, username, login, register, logout }
})
