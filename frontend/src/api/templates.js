/**
 * 对话模板 API 模块
 *
 * 封装对话模板的创建、查询、编辑和删除请求。
 * 内置模板（is_builtin=true）对所有用户可见，用户自建模板仅自己可见。
 */

import api from './index'

/** 获取模板列表（内置 + 用户自建） */
export function getTemplates() {
  return api.get('/templates')
}

/** 创建自定义对话模板（title/content 必填，category 可选） */
export function createTemplate(data) {
  return api.post('/templates', data)
}

/** 更新自定义模板（title/content/category 均可选） */
export function updateTemplate(templateId, data) {
  return api.put(`/templates/${templateId}`, data)
}

/** 删除自定义模板 */
export function deleteTemplate(templateId) {
  return api.delete(`/templates/${templateId}`)
}
