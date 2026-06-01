import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createConversation, getConversations, getMessages, streamChat } from '../api/chat'

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

    await streamChat(
      currentId.value,
      content,
      (token) => { messages.value[idx].content += token },
      () => { loading.value = false }
    )
  }

  return { conversations, currentId, messages, loading, loadConversations, newConversation, selectConversation, sendMessage }
})
