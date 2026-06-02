<script setup>
import { ref, nextTick, onUnmounted, computed } from 'vue'

defineProps({
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['send', 'stop'])
const input = ref('')
const textareaRef = ref(null)
const fileInputRef = ref(null)
const images = ref([]) // [{ name, dataUrl }]
const isRecording = ref(false)
let recognition = null

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
const speechSupported = computed(() => !!SpeechRecognition)

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 150) + 'px'
}

function handleSend() {
  const text = input.value.trim()
  if (!text && images.value.length === 0) return
  emit('send', { content: text, images: images.value.map(i => i.dataUrl) })
  input.value = ''
  images.value = []
  nextTick(() => {
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
  })
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

// === 语音输入 ===
function toggleVoice() {
  if (!SpeechRecognition) return
  if (isRecording.value) {
    stopVoice()
    return
  }
  recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.interimResults = true
  recognition.continuous = true

  let finalText = input.value

  recognition.onresult = (e) => {
    let interim = ''
    for (let i = e.resultIndex; i < e.results.length; i++) {
      if (e.results[i].isFinal) {
        finalText += e.results[i][0].transcript
      } else {
        interim += e.results[i][0].transcript
      }
    }
    input.value = finalText + interim
  }

  recognition.onerror = () => { isRecording.value = false }
  recognition.onend = () => { isRecording.value = false }

  recognition.start()
  isRecording.value = true
}

function stopVoice() {
  if (recognition) {
    recognition.stop()
    recognition = null
  }
  isRecording.value = false
}

onUnmounted(() => { stopVoice() })

// === 图片上传 ===
function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFileChange(e) {
  const files = Array.from(e.target.files || [])
  files.forEach(file => addImage(file))
  e.target.value = ''
}

function addImage(file) {
  if (!file.type.startsWith('image/')) return
  if (images.value.length >= 5) return
  const reader = new FileReader()
  reader.onload = (e) => {
    images.value.push({ name: file.name, dataUrl: e.target.result })
  }
  reader.readAsDataURL(file)
}

function removeImage(index) {
  images.value.splice(index, 1)
}

function handlePaste(e) {
  const items = Array.from(e.clipboardData?.items || [])
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      e.preventDefault()
      const file = item.getAsFile()
      if (file) addImage(file)
    }
  }
}
</script>

<template>
  <div class="input-area">
    <div v-if="images.length > 0" class="image-preview">
      <div v-for="(img, i) in images" :key="i" class="preview-item">
        <img :src="img.dataUrl" :alt="img.name" />
        <button class="remove-img" @click="removeImage(i)">&times;</button>
      </div>
    </div>
    <div class="input-wrapper">
      <button class="tool-btn" title="上传图片" @click="triggerFileInput">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <polyline points="21 15 16 10 5 21"/>
        </svg>
      </button>
      <input ref="fileInputRef" type="file" accept="image/*" multiple hidden @change="handleFileChange" />
      <button
        v-if="speechSupported"
        class="tool-btn"
        :class="{ recording: isRecording }"
        :title="isRecording ? '停止录音' : '语音输入'"
        @click="toggleVoice"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
        <span v-if="isRecording" class="pulse-dot"></span>
      </button>
      <textarea
        ref="textareaRef"
        v-model="input"
        class="input-box"
        placeholder="输入你的问题... (Enter 发送，Shift+Enter 换行)"
        rows="1"
        :disabled="loading"
        @input="autoResize"
        @keydown="handleKeydown"
        @paste="handlePaste"
      ></textarea>
      <button
        v-if="loading"
        class="stop-btn"
        @click="emit('stop')"
      >
        停止
      </button>
      <button
        v-else
        class="send-btn"
        :disabled="!input.trim() && images.length === 0"
        @click="handleSend"
      >
        发送
      </button>
    </div>
  </div>
</template>

<style scoped>
.input-area {
  padding: 16px 24px 24px;
  background: var(--bg-primary);
}

.image-preview {
  max-width: 800px;
  margin: 0 auto 8px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preview-item {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-img {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 18px;
  height: 18px;
  background: rgba(0,0,0,0.6);
  color: #fff;
  border: none;
  border-radius: 50%;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 8px;
  align-items: flex-end;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 12px 16px;
  transition: border-color 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--accent);
}

.tool-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  transition: color 0.15s;
  display: flex;
  align-items: center;
  position: relative;
  flex-shrink: 0;
}

.tool-btn:hover {
  color: var(--accent);
}

.tool-btn.recording {
  color: var(--danger);
}

.pulse-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 8px;
  height: 8px;
  background: var(--danger);
  border-radius: 50%;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

.input-box {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 15px;
  font-family: var(--font-sans);
  line-height: 1.5;
  resize: none;
  min-height: 24px;
  max-height: 150px;
}

.input-box::placeholder {
  color: var(--text-muted);
}

.send-btn {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-btn {
  background: var(--danger);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}

.stop-btn:hover {
  opacity: 0.85;
}

.loading-dot {
  animation: blink 1.2s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@media (max-width: 768px) {
  .input-area {
    padding: 12px 16px 16px;
  }

  .input-wrapper {
    padding: 10px 12px;
  }

  .input-box {
    font-size: 16px; /* prevent iOS zoom */
  }
}
</style>
