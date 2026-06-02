import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDashboardStats } from '../api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref(null)
  const loading = ref(false)

  async function loadStats() {
    loading.value = true
    try {
      const { data } = await getDashboardStats()
      stats.value = data
    } finally {
      loading.value = false
    }
  }

  return { stats, loading, loadStats }
})
