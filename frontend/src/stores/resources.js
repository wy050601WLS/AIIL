/**
 * 学习资料状态管理 Store
 *
 * 管理学习资料的加载、创建、编辑、删除和 AI 辅助搜索。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getResources, createResource, updateResource, deleteResource, askResources } from '../api/resources'

export const useResourcesStore = defineStore('resources', () => {
  const resources = ref([])      // 资料列表
  const loading = ref(false)     // 加载状态
  const asking = ref(false)      // AI 搜索状态
  const aiAnswer = ref('')       // AI 搜索回答
  const aiResults = ref([])      // AI 搜索关联的资料列表

  /** 从后端加载学习资料列表 */
  async function loadResources(params = {}) {
    loading.value = true
    try {
      const { data } = await getResources(params)
      resources.value = data
    } finally {
      loading.value = false
    }
  }

  /** 创建学习资料并添加到列表头部 */
  async function addResource(resourceData) {
    const { data } = await createResource(resourceData)
    resources.value.unshift(data)
    ElMessage.success('资料已保存')
    return data
  }

  /** 更新学习资料 */
  async function editResource(resourceId, updates) {
    const { data } = await updateResource(resourceId, updates)
    const idx = resources.value.findIndex(r => r.id === resourceId)
    if (idx !== -1) resources.value[idx] = data
    ElMessage.success('资料已更新')
    return data
  }

  /** 删除学习资料 */
  async function removeResource(resourceId) {
    await deleteResource(resourceId)
    resources.value = resources.value.filter(r => r.id !== resourceId)
    ElMessage.success('资料已删除')
  }

  /** AI 辅助搜索：发送问题，获取 AI 分析和推荐 */
  async function ask(question) {
    asking.value = true
    aiAnswer.value = ''
    aiResults.value = []
    try {
      const { data } = await askResources(question)
      aiAnswer.value = data.answer
      aiResults.value = data.resources || []
    } catch {
      ElMessage.error('AI 搜索失败，请稍后重试')
    } finally {
      asking.value = false
    }
  }

  /** 清除 AI 搜索结果 */
  function clearAiResults() {
    aiAnswer.value = ''
    aiResults.value = []
  }

  return {
    resources, loading, asking, aiAnswer, aiResults,
    loadResources, addResource, editResource, removeResource, ask, clearAiResults,
  }
})
