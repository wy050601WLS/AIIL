import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createConversation, getConversations, getMessages, streamChat, renameConversation, deleteConversation } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentId = ref(null)
  const messages = ref([])
  const loading = ref(false)

  async function loadConversations() {
    const { data } = await getConversations()
    conversations.value = data
  }

  async function newConversation(title = '新对话') {
    const { data } = await createConversation(title)
    conversations.value.unshift(data)
    currentId.value = data.id
    messages.value = []
    return data
  }

  async function selectConversation(id) {
    currentId.value = id
    const { data } = await getMessages(id)
    messages.value = data
  }

  async function sendMessage(content) {
    if (!currentId.value) {
      await newConversation(content.slice(0, 20))
    }

    messages.value.push({ role: 'user', content, created_at: new Date().toISOString() })

    const idx = messages.value.length
    messages.value.push({ role: 'assistant', content: '', created_at: new Date().toISOString() })
    loading.value = true

    try {
      await streamChat(
        currentId.value,
        content,
        (token) => { messages.value[idx].content += token },
        () => { loading.value = false }
      )
    } catch {
      loading.value = false
    }
  }

  async function rename(id, title) {
    const { data } = await renameConversation(id, title)
    const conv = conversations.value.find(c => c.id === id)
    if (conv) conv.title = data.title
  }

  async function remove(id) {
    await deleteConversation(id)
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (currentId.value === id) {
      currentId.value = null
      messages.value = []
    }
  }

  return { conversations, currentId, messages, loading, loadConversations, newConversation, selectConversation, sendMessage, rename, remove }
})
