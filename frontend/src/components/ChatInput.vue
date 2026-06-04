<!--
  ChatInput 组件 — 对话输入区

  功能：文本输入、图片上传（点击/粘贴）、语音输入、对话模板、发送/停止按钮
  Props: loading (Boolean) — AI 是否正在生成
  Events: send({content, images[]}) — 发送消息, stop — 停止生成
-->
<script setup>
import { ref, nextTick, onUnmounted, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTemplatesStore } from '../stores/templates'
import { useChatStore } from '../stores/chat'

defineProps({
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['send', 'stop'])
const templatesStore = useTemplatesStore()
const chatStore = useChatStore()
const input = ref('')               // 输入框文本
const textareaRef = ref(null)       // textarea DOM 引用
const fileInputRef = ref(null)      // 隐藏的 file input 引用
const images = ref([])              // 待发送的图片列表 [{ name, dataUrl }]
const isRecording = ref(false)      // 是否正在录音
const templatePopoverVisible = ref(false)  // 模板选择面板是否显示
const saveDialogVisible = ref(false)       // 保存模板对话框是否显示
const saveTitle = ref('')                  // 保存模板时的标题输入
const saveCategory = ref('')               // 保存模板时的分类输入
let recognition = null              // Web SpeechRecognition 实例

// 浏览器语音识别 API（兼容 webkit 前缀）
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
const speechSupported = computed(() => !!SpeechRecognition)

onMounted(() => { templatesStore.loadTemplates() })

/** 自动调整 textarea 高度（最大 150px） */
function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 150) + 'px'
}

/** 发送消息：触发 send 事件并清空输入 */
async function handleSend() {
  const text = input.value.trim()
  if (!text && images.value.length === 0) return
  // 如果有图片但当前模型不支持视觉，提示用户
  if (images.value.length > 0 && !chatStore.currentModelSupportsVision) {
    try {
      await ElMessageBox.confirm(
        `当前模型「${chatStore.currentModel}」不支持图片识别，图片将作为附件存储但 AI 不会分析。是否继续发送？`,
        '模型不支持图片',
        { confirmButtonText: '继续发送', cancelButtonText: '取消', type: 'warning' },
      )
    } catch {
      return
    }
  }
  emit('send', { content: text, images: images.value.map(i => i.dataUrl) })
  input.value = ''
  images.value = []
  nextTick(() => {
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
  })
}

/** Enter 发送，Shift+Enter 换行 */
function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

// ===== 语音输入 =====

/** 切换语音录制状态（开始/停止） */
function toggleVoice() {
  if (!SpeechRecognition) return
  if (isRecording.value) {
    stopVoice()
    return
  }
  recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'         // 中文识别
  recognition.interimResults = true   // 实时显示中间结果
  recognition.continuous = true       // 连续录音不停顿

  let finalText = input.value

  // 识别结果回调：final 结果追加到文本，interim 结果实时预览
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

/** 停止语音录制 */
function stopVoice() {
  if (recognition) {
    recognition.stop()
    recognition = null
  }
  isRecording.value = false
}

// 组件卸载时停止录音，避免内存泄漏
onUnmounted(() => { stopVoice() })

// ===== 图片上传 =====

/** 触发隐藏的 file input 点击 */
function triggerFileInput() {
  fileInputRef.value?.click()
}

/** 处理文件选择事件 */
function handleFileChange(e) {
  const files = Array.from(e.target.files || [])
  files.forEach(file => addImage(file))
  e.target.value = '' // 清空 input 允许重复选择同一文件
}

/** 将图片文件转为 base64 dataUrl 并添加到预览列表（最多 5 张） */
function addImage(file) {
  if (!file.type.startsWith('image/')) return
  if (images.value.length >= 5) return
  const reader = new FileReader()
  reader.onload = (e) => {
    images.value.push({ name: file.name, dataUrl: e.target.result })
  }
  reader.readAsDataURL(file)
}

/** 从预览列表中移除指定图片 */
function removeImage(index) {
  images.value.splice(index, 1)
}

/** 处理粘贴事件：如果剪贴板包含图片则自动添加 */
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

// ===== 对话模板 =====

/** 选择模板：将模板内容填充到输入框 */
function selectTemplate(content) {
  input.value = content
  templatePopoverVisible.value = false
  nextTick(() => {
    autoResize()
    textareaRef.value?.focus()
  })
}

/** 打开保存模板对话框 */
function openSaveDialog() {
  saveTitle.value = ''
  saveCategory.value = ''
  saveDialogVisible.value = true
}

/** 确认保存当前输入为模板 */
async function confirmSaveTemplate() {
  if (!saveTitle.value.trim()) {
    ElMessage.warning('请输入模板标题')
    return
  }
  await templatesStore.addTemplate(saveTitle.value.trim(), input.value.trim(), saveCategory.value.trim() || null)
  saveDialogVisible.value = false
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
      <el-popover
        v-model:visible="templatePopoverVisible"
        placement="top-start"
        :width="320"
        trigger="click"
      >
        <template #reference>
          <button class="tool-btn" title="对话模板">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </button>
        </template>
        <div class="template-panel">
          <div class="template-header">
            <span class="template-title">对话模板</span>
            <el-button v-if="input.trim()" type="primary" text size="small" @click="openSaveDialog">保存为模板</el-button>
          </div>
          <div v-if="templatesStore.loading" class="template-loading">加载中...</div>
          <div v-else-if="templatesStore.templates.length === 0" class="template-empty">暂无模板</div>
          <div v-else class="template-list">
            <div v-for="(items, cat) in templatesStore.groupedTemplates" :key="cat" class="template-group">
              <div class="template-group-label">{{ cat }}</div>
              <div
                v-for="t in items"
                :key="t.id"
                class="template-item"
                @click="selectTemplate(t.content)"
              >
                <span class="template-item-title">{{ t.title }}</span>
                <span class="template-item-preview">{{ t.content.slice(0, 30) }}...</span>
              </div>
            </div>
          </div>
        </div>
      </el-popover>
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
    <!-- 保存模板对话框 -->
    <el-dialog v-model="saveDialogVisible" title="保存为模板" width="400px" append-to-body>
      <el-form label-width="60px">
        <el-form-item label="标题">
          <el-input v-model="saveTitle" placeholder="给模板起个名字" maxlength="100" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="saveCategory" placeholder="如：翻译、解释、练习（可选）" maxlength="50" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input type="textarea" :model-value="input" :rows="3" disabled />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSaveTemplate">保存</el-button>
      </template>
    </el-dialog>
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

/* ===== 模板选择面板 ===== */

.template-panel {
  max-height: 360px;
  overflow-y: auto;
}

.template-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.template-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.template-loading,
.template-empty {
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  padding: 16px 0;
}

.template-group {
  margin-bottom: 8px;
}

.template-group-label {
  font-size: 12px;
  color: var(--text-muted);
  padding: 4px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 4px;
}

.template-item {
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.15s;
}

.template-item:hover {
  background: var(--bg-secondary);
}

.template-item-title {
  display: block;
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.template-item-preview {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
