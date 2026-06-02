/**
 * 认证 API 模块
 *
 * 封装用户注册、登录、获取/更新资料、修改密码的 HTTP 请求。
 */

import api from './index'

/** 用户注册 */
export function register(username, password) {
  return api.post('/auth/register', { username, password })
}

/** 用户登录，返回 JWT Token */
export function login(username, password) {
  return api.post('/auth/login', { username, password })
}

/** 修改密码（需提供旧密码和新密码） */
export function changePassword(oldPassword, newPassword) {
  return api.put('/auth/password', { old_password: oldPassword, new_password: newPassword })
}

/** 获取当前用户的个人信息 */
export function getProfile() {
  return api.get('/auth/profile')
}

/** 更新用户资料（昵称、头像、偏好设置） */
export function updateProfile(data) {
  return api.put('/auth/profile', data)
}
