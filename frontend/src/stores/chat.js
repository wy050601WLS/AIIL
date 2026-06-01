import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createConversation, getConversations, getMessages, streamChat, renameConversation, deleteConversation, getModels, exportConversation } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentId = ref(null)
  const messages = ref([])
  const loading = ref(false)
  const models = ref([])
  const currentModel = ref(localStorage.getItem('model') || '')

  async function loadModels() {
    try {
      const { data } = await getModels()
      models.value = data.models
      if (!currentModel.value && data.default) {
        currentModel.value = data.default
      }
    } catch {
      // ignore
    }
  }

  function setModel(modelId) {
    currentModel.value = modelId
    localStorage.setItem('model', modelId)
  }

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
        () => { loading.value = false },
        currentModel.value || undefined,
      )
    } catch {
      loading.value = false
    }
  }

  async function regenerate() {
    if (!currentId.value || loading.value) return
    const lastUserIdx = [...messages.value].reverse().findIndex(m => m.role === 'user')
    if (lastUserIdx === -1) return
    const lastUserContent = messages.value[messages.value.length - 1 - lastUserIdx].content
    if (messages.value[messages.value.length - 1].role === 'assistant') {
      messages.value.pop()
    }
    const idx = messages.value.length
    messages.value.push({ role: 'assistant', content: '', created_at: new Date().toISOString() })
    loading.value = true
    try {
      await streamChat(
        currentId.value,
        lastUserContent,
        (token) => { messages.value[idx].content += token },
        () => { loading.value = false },
        currentModel.value || undefined,
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

  async function exportCurrent() {
    if (!currentId.value) return
    await exportConversation(currentId.value)
  }

  return {
    conversations, currentId, messages, loading, models, currentModel,
    loadConversations, newConversation, selectConversation, sendMessage,
    rename, remove, regenerate, loadModels, setModel, exportCurrent,
  }
})
