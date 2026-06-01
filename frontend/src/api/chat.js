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

export async function streamChat(conversationId, content, onToken, onDone) {
  const token = localStorage.getItem('token')
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ conversation_id: conversationId, content }),
  })

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
        onToken(data)
      }
    }
  }
  onDone?.()
}
