/**
 * 知识卡片状态管理 Store
 *
 * 管理知识卡片的加载、添加和删除操作。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createCard, getCards, updateCard, deleteCard } from '../api/cards'

export const useCardsStore = defineStore('cards', () => {
  const cards = ref([])      // 知识卡片列表
  const loading = ref(false) // 加载状态

  /** 从后端加载知识卡片列表 */
  async function loadCards() {
    loading.value = true
    try {
      const { data } = await getCards()
      cards.value = data
    } catch {
      ElMessage.error('加载卡片失败')
    } finally {
      loading.value = false
    }
  }

  /** 创建知识卡片并添加到列表头部 */
  async function addCard(content, source, tags) {
    try {
      const { data } = await createCard({ content, source, tags })
      cards.value.unshift(data)
      ElMessage.success('已保存为知识卡片')
      return data
    } catch {
      ElMessage.error('保存卡片失败')
      return null
    }
  }

  /** 更新知识卡片内容和标签 */
  async function editCard(cardId, updates) {
    try {
      const { data } = await updateCard(cardId, updates)
      const idx = cards.value.findIndex(c => c.id === cardId)
      if (idx !== -1) cards.value[idx] = data
      ElMessage.success('卡片已更新')
      return data
    } catch {
      ElMessage.error('更新卡片失败')
      return null
    }
  }

  /** 删除知识卡片并从列表中移除 */
  async function removeCard(cardId) {
    try {
      await deleteCard(cardId)
      cards.value = cards.value.filter(c => c.id !== cardId)
      ElMessage.success('卡片已删除')
    } catch {
      ElMessage.error('删除卡片失败')
    }
  }

  return { cards, loading, loadCards, addCard, editCard, removeCard }
})
