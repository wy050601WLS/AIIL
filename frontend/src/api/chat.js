import api from './index'

export function createConversation(title) {
  return api.post('/conversations', { title })
}

export function getConversations() {
  return api.get('/conversations')
}

export function getMessages(conversationId) {
  return api.get(`/conversations/${conversationId}/messages`)
}

export function renameConversation(conversationId, title) {
  return api.put(`/conversations/${conversationId}`, { title })
}

export function deleteConversation(conversationId) {
  return api.delete(`/conversations/${conversationId}`)
}

export function getModels() {
  return api.get('/models')
}

export function editMessage(messageId, content) {
  return api.put(`/messages/${messageId}`, { content })
}

export function deleteMessage(messageId) {
  return api.delete(`/messages/${messageId}`)
}

export function pinConversation(conversationId) {
  return api.put(`/conversations/${conversationId}/pin`)
}

export function archiveConversation(conversationId) {
  return api.put(`/conversations/${conversationId}/archive`)
}

export function updateSystemPrompt(conversationId, systemPrompt) {
  return api.put(`/conversations/${conversationId}/system-prompt`, { system_prompt: systemPrompt })
}

export async function exportConversation(conversationId) {
  const token = localStorage.getItem('token')
  const res = await fetch(`/api/conversations/${conversationId}/export`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `conversation-${conversationId}.md`
  a.click()
  URL.revokeObjectURL(url)
}

export async function streamChat(conversationId, content, onToken, onDone, model, regenerate = false, signal, images) {
  const token = localStorage.getItem('token')
  const body = { conversation_id: conversationId, content, model, regenerate }
  if (images && images.length > 0) body.images = images
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
      signal,
    })

    if (!res.ok) {
      onDone?.()
      return
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            onDone?.()
            return
          }
          if (data) onToken(data)
        }
      }
    }
  } catch {
    // stream interrupted
  } finally {
    onDone?.()
  }
}
