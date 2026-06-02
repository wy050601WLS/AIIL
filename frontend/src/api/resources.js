/**
 * 学习资料 API 模块
 *
 * 封装学习资料的创建、查询、编辑、删除和 AI 辅助搜索请求。
 */

import api from './index'

/** 创建学习资料（title 必填，其余可选） */
export function createResource(data) {
  return api.post('/resources', data)
}

/** 获取学习资料列表，支持 category/resource_type 过滤 */
export function getResources(params = {}) {
  return api.get('/resources', { params })
}

/** 更新学习资料 */
export function updateResource(resourceId, data) {
  return api.put(`/resources/${resourceId}`, data)
}

/** 删除学习资料 */
export function deleteResource(resourceId) {
  return api.delete(`/resources/${resourceId}`)
}

/** AI 辅助搜索：发送问题，返回 AI 分析和推荐 */
export function askResources(question) {
  return api.post('/resources/ask', { question })
}
