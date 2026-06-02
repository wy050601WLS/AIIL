import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createCard, getCards, deleteCard } from '../api/cards'

export const useCardsStore = defineStore('cards', () => {
  const cards = ref([])
  const loading = ref(false)

  async function loadCards() {
    loading.value = true
    try {
      const { data } = await getCards()
      cards.value = data
    } finally {
      loading.value = false
    }
  }

  async function addCard(content, source, tags) {
    const { data } = await createCard({ content, source, tags })
    cards.value.unshift(data)
    ElMessage.success('已保存为知识卡片')
    return data
  }

  async function removeCard(cardId) {
    await deleteCard(cardId)
    cards.value = cards.value.filter(c => c.id !== cardId)
    ElMessage.success('卡片已删除')
  }

  return { cards, loading, loadCards, addCard, removeCard }
})
