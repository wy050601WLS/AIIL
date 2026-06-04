<!--
  KnowledgeDetail 视图 — 知识库文档详情页

  功能：展示文档全文内容，支持编辑标题/标签
-->
<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useKnowledgeStore } from '../stores/knowledge'

const route = useRoute()
const router = useRouter()
const knowledgeStore = useKnowledgeStore()

const editing = ref(false)
const editTitle = ref('')
const editTags = ref('')
const editVisibility = ref('public')

const visibilities = [
  { value: 'public', label: '公共', desc: '所有人可见' },
  { value: 'private', label: '私人', desc: '仅自己可见' },
  { value: 'draft', label: '草稿', desc: '仅自己可见，未完成' },
]

const fileTypeLabels = {
  pdf: 'PDF',
  docx: 'Word',
  txt: '文本',
  md: 'Markdown',
}

onMounted(async () => {
  const docId = Number(route.params.id)
  if (!docId || isNaN(docId)) {
    ElMessage.error('无效的文档 ID')
    router.push('/resources')
    return
  }
  await knowledgeStore.loadDocument(docId)
})

function startEdit() {
  const doc = knowledgeStore.currentDoc
  if (!doc) return
  editTitle.value = doc.title
  editTags.value = doc.tags || ''
  editVisibility.value = doc.visibility || 'public'
  editing.value = true
}

async function saveEdit() {
  if (!editTitle.value.trim()) {
    ElMessage.warning('标题不能为空')
    return
  }
  await knowledgeStore.editDocument(knowledgeStore.currentDoc.id, {
    title: editTitle.value.trim(),
    tags: editTags.value.trim() || null,
    visibility: editVisibility.value,
  })
  editing.value = false
}

function cancelEdit() {
  editing.value = false
}

function goBack() {
  router.push('/resources')
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
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function tagList(tags) {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}
</script>

<template>
  <div class="detail-page">
    <div v-if="knowledgeStore.loading && !knowledgeStore.currentDoc" class="loading">加载中...</div>
    <template v-else-if="knowledgeStore.currentDoc">
      <div class="detail-header">
        <el-button text @click="goBack" class="back-btn">← 返回列表</el-button>
      </div>

      <div class="detail-meta">
        <template v-if="!editing">
          <h1 class="doc-title">{{ knowledgeStore.currentDoc.title }}</h1>
          <div class="meta-row">
            <span class="meta-badge">{{ fileTypeLabels[knowledgeStore.currentDoc.file_type] || knowledgeStore.currentDoc.file_type }}</span>
            <span class="visibility-badge" :class="`vis-${knowledgeStore.currentDoc.visibility || 'public'}`">{{ visibilities.find(v => v.value === knowledgeStore.currentDoc.visibility)?.label || '公共' }}</span>
            <span class="meta-size">{{ formatSize(knowledgeStore.currentDoc.file_size) }}</span>
            <span class="meta-time">{{ formatTime(knowledgeStore.currentDoc.created_at) }}</span>
            <el-button text size="small" @click="startEdit">编辑</el-button>
          </div>
          <div v-if="knowledgeStore.currentDoc.tags" class="doc-tags">
            <span v-for="tag in tagList(knowledgeStore.currentDoc.tags)" :key="tag" class="tag-chip tag-chip--accent">{{ tag }}</span>
          </div>
        </template>
        <template v-else>
          <div class="edit-form">
            <div class="edit-row">
              <label>标题</label>
              <input v-model="editTitle" class="edit-input" maxlength="200" />
            </div>
            <div class="edit-row">
              <label>标签</label>
              <input v-model="editTags" class="edit-input" placeholder="逗号分隔" maxlength="500" />
            </div>
            <div class="edit-row">
              <label>可见性</label>
              <select v-model="editVisibility" class="edit-input">
                <option v-for="v in visibilities" :key="v.value" :value="v.value">{{ v.label }} — {{ v.desc }}</option>
              </select>
            </div>
            <div class="edit-actions">
              <el-button type="primary" size="small" @click="saveEdit">保存</el-button>
              <el-button text size="small" @click="cancelEdit">取消</el-button>
            </div>
          </div>
        </template>
      </div>

      <div class="detail-content">
        <div v-if="knowledgeStore.currentDoc.content_text" class="content-text">{{ knowledgeStore.currentDoc.content_text }}</div>
        <div v-else class="content-empty">文档内容解析失败或为空</div>
      </div>
    </template>
    <div v-else class="empty">文档不存在</div>
  </div>
</template>

<style scoped>
.detail-page {
  max-width: var(--page-max-width);
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
  min-height: 100vh;
  background: var(--bg-primary);
}

.loading, .empty {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--text-base);
  padding: 60px 0;
}

.detail-header {
  margin-bottom: 20px;
}

.back-btn {
  color: var(--text-secondary);
  font-size: var(--text-base);
}

.back-btn:hover {
  color: var(--accent);
}

.detail-meta {
  margin-bottom: var(--space-lg);
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.doc-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin-bottom: 10px;
}

.meta-badge {
  background: var(--bg-tertiary);
  padding: 2px var(--space-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
}

.doc-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.edit-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.edit-row label {
  font-size: var(--text-base);
  color: var(--text-secondary);
  width: 40px;
  flex-shrink: 0;
}

.edit-input {
  flex: 1;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-base);
  padding: 6px 10px;
  outline: none;
  font-family: inherit;
}

.edit-input:focus {
  border-color: var(--accent);
}

.edit-actions {
  display: flex;
  gap: var(--space-sm);
}

.detail-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.content-text {
  font-size: var(--text-base);
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.content-empty {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--text-base);
  padding: 40px 0;
}

@media (max-width: 768px) {
  .detail-page {
    padding: 20px 16px;
  }

  .meta-row {
    flex-wrap: wrap;
  }
}
</style>
