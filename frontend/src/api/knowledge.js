/**
 * 知识库 API 模块
 *
 * 提供文档上传、列表、详情、更新和删除的请求函数。
 */

import api from './index'

/** 上传文档文件（multipart/form-data） */
export function uploadDocument(file, title, tags, visibility) {
  const formData = new FormData()
  formData.append('file', file)
  if (title) formData.append('title', title)
  if (tags) formData.append('tags', tags)
  if (visibility) formData.append('visibility', visibility)
  return api.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 获取文档列表（支持关键词搜索） */
export function getDocuments(params = {}) {
  return api.get('/knowledge', { params })
}

/** 获取文档详情 */
export function getDocument(docId) {
  return api.get(`/knowledge/${docId}`)
}

/** 更新文档标题/标签 */
export function updateDocument(docId, data) {
  return api.put(`/knowledge/${docId}`, data)
}

/** 删除文档 */
export function deleteDocument(docId) {
  return api.delete(`/knowledge/${docId}`)
}
