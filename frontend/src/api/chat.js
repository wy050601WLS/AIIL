/**
 * 对话与会话 API 模块
 *
 * 封装会话管理（CRUD/置顶/归档/导出）和 AI 对话（SSE 流式/消息编辑）的请求。
 * 其中 streamChat 使用原生 fetch 而非 Axios，因为需要读取 SSE 流。
 */

import api from './index'

/** 创建新会话 */
export function createConversation(title) {
  return api.post('/conversations', { title })
}

/** 获取会话列表 */
export function getConversations() {
  return api.get('/conversations')
}

/** 获取指定会话的消息列表（支持分页：skip 跳过，limit 限制数量） */
export function getMessages(conversationId, skip = 0, limit = 0) {
  const params = {}
  if (skip > 0) params.skip = skip
  if (limit > 0) params.limit = limit
  return api.get(`/conversations/${conversationId}/messages`, { params })
}

/** 重命名会话 */
export function renameConversation(conversationId, title) {
  return api.put(`/conversations/${conversationId}`, { title })
}

/** 删除会话 */
export function deleteConversation(conversationId) {
  return api.delete(`/conversations/${conversationId}`)
}

/** 获取可用的 AI 模型列表 */
export function getModels() {
  return api.get('/models')
}

/** 编辑消息内容 */
export function editMessage(messageId, content) {
  return api.put(`/messages/${messageId}`, { content })
}

/** 删除单条消息 */
export function deleteMessage(messageId) {
  return api.delete(`/messages/${messageId}`)
}

/** 切换会话置顶状态 */
export function pinConversation(conversationId) {
  return api.put(`/conversations/${conversationId}/pin`)
}

/** 切换会话归档状态 */
export function archiveConversation(conversationId) {
  return api.put(`/conversations/${conversationId}/archive`)
}

/** 导出会话为 Markdown 文件并触发下载 */
export async function exportConversation(conversationId) {
  const token = localStorage.getItem('token')
  const res = await fetch(`/api/conversations/${conversationId}/export`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '导出失败' }))
    throw new Error(err.detail || '导出失败')
  }
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `conversation-${conversationId}.md`
  a.click()
  URL.revokeObjectURL(url)
}

/**
 * SSE 真流式对话
 *
 * 使用原生 fetch 读取 Server-Sent Events 流，逐 token 回调。
 * 后端采用真流式：收到 AI 每个 chunk 后立即转发，实现低延迟逐 token 显示。
 *
 * @param {number} conversationId - 会话 ID
 * @param {string} content - 用户消息内容
 * @param {Function} onToken - 每收到一个 token 时的回调
 * @param {Function} onDone - 流结束时的回调
 * @param {string} [model] - 指定 AI 模型 ID
 * @param {boolean} [regenerate=false] - 是否为重新生成
 * @param {AbortSignal} [signal] - 用于中断请求的 AbortSignal
 * @param {string[]} [images] - base64 图片列表（多模态输入）
 */
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
      const errBody = await res.json().catch(() => ({ detail: '请求失败' }))
      onDone?.()
      throw new Error(errBody.detail || `请求失败 (${res.status})`)
    }

    // 读取 SSE 流：逐块读取并解析 "data: ..." 格式
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() // 保留未完成的行

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

    // 处理缓冲区中剩余的数据
    if (buffer.trim()) {
      const lines = buffer.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data !== '[DONE]' && data) onToken(data)
        }
      }
    }
  } catch {
    // 流被中断或网络错误，静默处理
  } finally {
    onDone?.()
  }
}
