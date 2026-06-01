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

export async function streamChat(conversationId, content, onToken, onDone) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ conversation_id: conversationId, content }),
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
