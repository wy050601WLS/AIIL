/**
 * 学习面板状态管理 Store
 *
 * 加载并缓存学习统计数据（对话数、消息数、卡片数、活跃天数、趋势图、标签）。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardStats } from '../api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref(null)      // 统计数据对象
  const loading = ref(false)   // 加载状态

  /** 从后端加载学习面板统计数据 */
  async function loadStats() {
    loading.value = true
    try {
      const { data } = await getDashboardStats()
      stats.value = data
    } catch {
      ElMessage.error('加载统计数据失败')
    } finally {
      loading.value = false
    }
  }

  return { stats, loading, loadStats }
})
