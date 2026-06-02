/**
 * 对话模板状态管理 Store
 *
 * 管理对话模板的加载、创建、编辑和删除操作。
 * 模板按分类分组，支持快速选择填充到输入框。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getTemplates, createTemplate, updateTemplate, deleteTemplate } from '../api/templates'

export const useTemplatesStore = defineStore('templates', () => {
  const templates = ref([])    // 模板列表
  const loading = ref(false)   // 加载状态

  /** 按分类分组的模板列表（computed，自动更新） */
  const groupedTemplates = computed(() => {
    const groups = {}
    for (const t of templates.value) {
      const cat = t.category || '其他'
      if (!groups[cat]) groups[cat] = []
      groups[cat].push(t)
    }
    return groups
  })

  /** 从后端加载模板列表 */
  async function loadTemplates() {
    loading.value = true
    try {
      const { data } = await getTemplates()
      templates.value = data
    } finally {
      loading.value = false
    }
  }

  /** 创建自定义模板并添加到列表 */
  async function addTemplate(title, content, category) {
    const { data } = await createTemplate({ title, content, category })
    templates.value.push(data)
    ElMessage.success('模板已保存')
    return data
  }

  /** 更新自定义模板 */
  async function editTemplate(templateId, updates) {
    const { data } = await updateTemplate(templateId, updates)
    const idx = templates.value.findIndex(t => t.id === templateId)
    if (idx !== -1) templates.value[idx] = data
    ElMessage.success('模板已更新')
    return data
  }

  /** 删除自定义模板 */
  async function removeTemplate(templateId) {
    await deleteTemplate(templateId)
    templates.value = templates.value.filter(t => t.id !== templateId)
    ElMessage.success('模板已删除')
  }

  return { templates, loading, groupedTemplates, loadTemplates, addTemplate, editTemplate, removeTemplate }
})
