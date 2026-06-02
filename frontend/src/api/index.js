/**
 * API 客户端模块
 *
 * 创建 Axios 实例并配置：
 * - 请求拦截器：自动附加 JWT Token 到 Authorization 头
 * - 响应拦截器：401 时清除 Token 并跳转登录页
 */

import axios from 'axios'

// 创建 Axios 实例，baseURL 指向后端 API 前缀
const api = axios.create({
  baseURL: '/api',
})

// 请求拦截器：从 localStorage 读取 Token 并附加到请求头
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：遇到 401 自动清除 Token 并跳转登录页
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
