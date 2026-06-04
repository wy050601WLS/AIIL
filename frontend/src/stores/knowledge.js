/**
 * 知识库 Pinia Store
 *
 * 管理文档列表状态和 CRUD 操作。
 */

import { ref } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import { uploadDocument, getDocuments, getDocument, updateDocument, deleteDocument } from '../api/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const documents = ref([])
  const currentDoc = ref(null)
  const loading = ref(false)
  const uploading = ref(false)

  /** 加载文档列表 */
  async function loadDocuments(keyword) {
    loading.value = true
    try {
      const params = {}
      if (keyword) params.keyword = keyword
      const { data } = await getDocuments(params)
      documents.value = data
    } catch {
      ElMessage.error('加载文档列表失败')
    } finally {
      loading.value = false
    }
  }

  /** 上传文档 */
  async function addDocument(file, title, tags, visibility) {
    uploading.value = true
    try {
      const { data } = await uploadDocument(file, title, tags, visibility)
      documents.value.unshift(data)
      ElMessage.success('文档上传成功')
      return data
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '上传失败')
      return null
    } finally {
      uploading.value = false
    }
  }

  /** 加载文档详情 */
  async function loadDocument(docId) {
    loading.value = true
    try {
      const { data } = await getDocument(docId)
      currentDoc.value = data
      return data
    } catch {
      ElMessage.error('加载文档详情失败')
      return null
    } finally {
      loading.value = false
    }
  }

  /** 更新文档 */
  async function editDocument(docId, updates) {
    try {
      const { data } = await updateDocument(docId, updates)
      const idx = documents.value.findIndex(d => d.id === docId)
      if (idx !== -1) documents.value[idx] = data
      if (currentDoc.value?.id === docId) currentDoc.value = data
      ElMessage.success('文档已更新')
    } catch {
      ElMessage.error('更新失败')
    }
  }

  /** 删除文档 */
  async function removeDocument(docId) {
    try {
      await deleteDocument(docId)
      documents.value = documents.value.filter(d => d.id !== docId)
      ElMessage.success('文档已删除')
    } catch {
      ElMessage.error('删除失败')
    }
  }

  return {
    documents, currentDoc, loading, uploading,
    loadDocuments, addDocument, loadDocument, editDocument, removeDocument,
  }
})
