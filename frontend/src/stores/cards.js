/**
 * 知识卡片状态管理 Store
 *
 * 管理知识卡片的加载、添加和删除操作。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createCard, getCards, deleteCard } from '../api/cards'

export const useCardsStore = defineStore('cards', () => {
  const cards = ref([])      // 知识卡片列表
  const loading = ref(false) // 加载状态

  /** 从后端加载知识卡片列表 */
  async function loadCards() {
    loading.value = true
    try {
      const { data } = await getCards()
      cards.value = data
    } finally {
      loading.value = false
    }
  }

  /** 创建知识卡片并添加到列表头部 */
  async function addCard(content, source, tags) {
    const { data } = await createCard({ content, source, tags })
    cards.value.unshift(data)
    ElMessage.success('已保存为知识卡片')
    return data
  }

  /** 删除知识卡片并从列表中移除 */
  async function removeCard(cardId) {
    await deleteCard(cardId)
    cards.value = cards.value.filter(c => c.id !== cardId)
    ElMessage.success('卡片已删除')
  }

  return { cards, loading, loadCards, addCard, removeCard }
})
