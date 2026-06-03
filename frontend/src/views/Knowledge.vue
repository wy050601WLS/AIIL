<!--
  Knowledge 视图 — 知识库文档列表页

  功能：展示已上传的文档列表，支持上传文件、关键词搜索、删除
-->
<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useKnowledgeStore } from '../stores/knowledge'

const knowledgeStore = useKnowledgeStore()
const router = useRouter()

const searchKeyword = ref('')
const uploadDialogVisible = ref(false)
const uploadTitle = ref('')
const uploadTags = ref('')
const selectedFile = ref(null)

const fileTypeIcons = {
  pdf: '📄',
  docx: '📝',
  txt: '📃',
  md: '📑',
}

const fileTypeLabels = {
  pdf: 'PDF',
  docx: 'Word',
  txt: '文本',
  md: 'Markdown',
}

onMounted(() => knowledgeStore.loadDocuments())

function handleSearch() {
  knowledgeStore.loadDocuments(searchKeyword.value.trim() || undefined)
}

function clearSearch() {
  searchKeyword.value = ''
  knowledgeStore.loadDocuments()
}

function openUploadDialog() {
  selectedFile.value = null
  uploadTitle.value = ''
  uploadTags.value = ''
  uploadDialogVisible.value = true
}

function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (file) {
    selectedFile.value = file
    if (!uploadTitle.value) {
      uploadTitle.value = file.name.replace(/\.[^.]+$/, '')
    }
  }
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  const doc = await knowledgeStore.addDocument(
    selectedFile.value,
    uploadTitle.value.trim() || undefined,
    uploadTags.value.trim() || undefined,
  )
  if (doc) {
    uploadDialogVisible.value = false
  }
}

function goToDetail(id) {
  router.push(`/knowledge/${id}`)
}

async function handleDelete(doc) {
  try {
    await ElMessageBox.confirm(`确定删除文档「${doc.title}」？`, '删除文档', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await knowledgeStore.removeDocument(doc.id)
  } catch {
    // 用户取消
  }
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function tagList(tags) {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}
</script>

<template>
  <div class="knowledge-page">
    <div class="knowledge-header">
      <h1>知识库</h1>
      <p class="subtitle">上传学习文档，随时查阅和搜索</p>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input
        v-model="searchKeyword"
        class="search-input"
        placeholder="搜索文档标题或标签..."
        @keydown.enter="handleSearch"
      />
      <el-button @click="handleSearch">搜索</el-button>
      <el-button text @click="clearSearch">重置</el-button>
      <div class="search-spacer"></div>
      <el-button type="primary" @click="openUploadDialog">+ 上传文档</el-button>
    </div>

    <!-- 文档列表 -->
    <div v-if="knowledgeStore.loading && knowledgeStore.documents.length === 0" class="empty">加载中...</div>
    <div v-else-if="knowledgeStore.documents.length === 0" class="empty">
      {{ searchKeyword ? '没有匹配的文档' : '还没有文档，点击上方「+ 上传文档」开始' }}
    </div>

    <div class="doc-grid">
      <div v-for="doc in knowledgeStore.documents" :key="doc.id" class="doc-item" @click="goToDetail(doc.id)">
        <div class="doc-header-row">
          <span class="doc-icon">{{ fileTypeIcons[doc.file_type] || '📄' }}</span>
          <span class="doc-title">{{ doc.title }}</span>
          <span class="doc-type-badge">{{ fileTypeLabels[doc.file_type] || doc.file_type }}</span>
        </div>
        <div v-if="doc.content_text" class="doc-preview">{{ doc.content_text.slice(0, 120) }}...</div>
        <div v-if="doc.tags" class="doc-tags">
          <span v-for="tag in tagList(doc.tags)" :key="tag" class="tag-chip">{{ tag }}</span>
        </div>
        <div class="doc-footer">
          <span class="doc-size">{{ formatSize(doc.file_size) }}</span>
          <span class="doc-time">{{ formatTime(doc.created_at) }}</span>
          <el-button text size="small" class="doc-delete" @click.stop="handleDelete(doc)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文档" width="480px" append-to-body>
      <el-form label-width="60px">
        <el-form-item label="文件">
          <input type="file" accept=".pdf,.docx,.txt,.md" @change="handleFileChange" />
          <div v-if="selectedFile" class="file-info">
            {{ selectedFile.name }} ({{ formatSize(selectedFile.size) }})
          </div>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="uploadTitle" placeholder="文档标题（默认取文件名）" maxlength="200" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="uploadTags" placeholder="标签（逗号分隔）" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="knowledgeStore.uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.knowledge-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px;
  min-height: 100vh;
  background: var(--bg-primary);
}

.knowledge-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 24px;
}

.search-bar {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 14px;
  padding: 8px 14px;
  outline: none;
  font-family: inherit;
}

.search-input:focus {
  border-color: var(--accent);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-spacer {
  flex: 1;
}

.empty {
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
  padding: 60px 0;
}

.doc-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.doc-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.15s;
}

.doc-item:hover {
  box-shadow: var(--shadow);
}

.doc-header-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.doc-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.doc-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-type-badge {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 8px;
  flex-shrink: 0;
}

.doc-preview {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 8px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.doc-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.tag-chip {
  font-size: 11px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  padding: 2px 8px;
  border-radius: 10px;
}

.doc-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.doc-size {
  flex-shrink: 0;
}

.doc-time {
  flex: 1;
}

.doc-delete {
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 6px;
  height: auto;
}

.doc-delete:hover {
  color: var(--danger);
}

.file-info {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .knowledge-page {
    padding: 20px 16px;
  }

  .search-bar {
    flex-wrap: wrap;
  }

  .search-spacer {
    display: none;
  }
}
</style>
