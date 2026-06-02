<!--
  Resources 视图 — 学习资料库页

  功能：展示学习资料列表，支持分类/类型筛选、关键词搜索、AI 辅助查找、增删改
-->
<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useResourcesStore } from '../stores/resources'

const resourcesStore = useResourcesStore()

const filterCategory = ref('')
const filterType = ref('')
const filterKeyword = ref('')
const askQuestion = ref('')

// 新增/编辑对话框状态
const dialogVisible = ref(false)
const editingId = ref(null)
const form = ref({ title: '', url: '', description: '', category: '', resource_type: '', tags: '' })

const categories = ['编程', '数学', '英语', '设计', '科学', '历史', '其他']
const types = [
  { value: 'article', label: '文章' },
  { value: 'video', label: '视频' },
  { value: 'course', label: '课程' },
  { value: 'tool', label: '工具' },
  { value: 'book', label: '书籍' },
  { value: 'other', label: '其他' },
]

const filteredResources = computed(() => {
  let list = resourcesStore.resources
  if (filterCategory.value) list = list.filter(r => r.category === filterCategory.value)
  if (filterType.value) list = list.filter(r => r.resource_type === filterType.value)
  if (filterKeyword.value.trim()) {
    const q = filterKeyword.value.toLowerCase()
    list = list.filter(r =>
      r.title.toLowerCase().includes(q) ||
      (r.description || '').toLowerCase().includes(q) ||
      (r.tags || '').toLowerCase().includes(q)
    )
  }
  return list
})

onMounted(() => resourcesStore.loadResources())

function openAddDialog() {
  editingId.value = null
  form.value = { title: '', url: '', description: '', category: '', resource_type: '', tags: '' }
  dialogVisible.value = true
}

function openEditDialog(resource) {
  editingId.value = resource.id
  form.value = {
    title: resource.title,
    url: resource.url || '',
    description: resource.description || '',
    category: resource.category || '',
    resource_type: resource.resource_type || '',
    tags: resource.tags || '',
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.title.trim()) {
    ElMessage.warning('请输入资料标题')
    return
  }
  const data = {
    ...form.value,
    url: form.value.url.trim() || null,
    description: form.value.description.trim() || null,
    category: form.value.category || null,
    resource_type: form.value.resource_type || null,
    tags: form.value.tags.trim() || null,
  }
  if (editingId.value) {
    await resourcesStore.editResource(editingId.value, data)
  } else {
    await resourcesStore.addResource(data)
  }
  dialogVisible.value = false
}

async function handleDelete(resource) {
  try {
    await ElMessageBox.confirm('确定删除这条学习资料？', '删除资料', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await resourcesStore.removeResource(resource.id)
  } catch {
    // 用户取消
  }
}

async function handleAsk() {
  const q = askQuestion.value.trim()
  if (!q) return
  await resourcesStore.ask(q)
}

function clearFilters() {
  filterCategory.value = ''
  filterType.value = ''
  filterKeyword.value = ''
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

function typeLabel(type) {
  const found = types.find(t => t.value === type)
  return found ? found.label : type
}
</script>

<template>
  <div class="resources-page">
    <div class="resources-header">
      <h1>学习资料库</h1>
      <p class="subtitle">收集和管理学习资料，AI 帮你快速查找</p>
    </div>

    <!-- AI 搜索区 -->
    <div class="ai-search-section">
      <div class="ai-search-input">
        <input
          v-model="askQuestion"
          class="ask-input"
          placeholder="问问 AI：我有哪些编程相关的资料？"
          @keydown.enter="handleAsk"
        />
        <el-button type="primary" :loading="resourcesStore.asking" @click="handleAsk">AI 搜索</el-button>
      </div>
      <div v-if="resourcesStore.aiAnswer" class="ai-answer">
        <div class="ai-answer-label">AI 分析</div>
        <div class="ai-answer-text">{{ resourcesStore.aiAnswer }}</div>
        <el-button text size="small" @click="resourcesStore.clearAiResults()">收起</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select v-model="filterCategory" placeholder="分类" size="small" clearable style="width: 120px;">
        <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
      </el-select>
      <el-select v-model="filterType" placeholder="类型" size="small" clearable style="width: 120px;">
        <el-option v-for="t in types" :key="t.value" :label="t.label" :value="t.value" />
      </el-select>
      <input v-model="filterKeyword" class="keyword-input" placeholder="搜索标题/描述/标签" />
      <el-button text size="small" @click="clearFilters">重置</el-button>
      <div class="filter-spacer"></div>
      <el-button type="primary" size="small" @click="openAddDialog">+ 添加资料</el-button>
    </div>

    <!-- 列表 -->
    <div v-if="resourcesStore.loading && resourcesStore.resources.length === 0" class="empty">加载中...</div>
    <div v-else-if="filteredResources.length === 0" class="empty">
      {{ filterCategory || filterType || filterKeyword ? '没有匹配的资料' : '还没有学习资料，点击上方「+ 添加资料」开始收集' }}
    </div>

    <div class="resources-grid">
      <div v-for="resource in filteredResources" :key="resource.id" class="resource-item">
        <div class="resource-header-row">
          <span class="resource-title">
            <a v-if="resource.url" :href="resource.url" target="_blank" rel="noopener">{{ resource.title }}</a>
            <span v-else>{{ resource.title }}</span>
          </span>
          <span v-if="resource.resource_type" class="resource-type-badge">{{ typeLabel(resource.resource_type) }}</span>
        </div>
        <div v-if="resource.description" class="resource-desc">{{ resource.description }}</div>
        <div class="resource-meta">
          <span v-if="resource.category" class="resource-category">{{ resource.category }}</span>
          <span v-for="tag in tagList(resource.tags)" :key="tag" class="tag-chip">{{ tag }}</span>
        </div>
        <div class="resource-footer">
          <span class="resource-time">{{ formatTime(resource.created_at) }}</span>
          <el-button text size="small" class="resource-edit" @click="openEditDialog(resource)">编辑</el-button>
          <el-button text size="small" class="resource-delete" @click="handleDelete(resource)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑资料' : '添加资料'"
      width="500px"
      append-to-body
    >
      <el-form label-width="60px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="资料标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="链接">
          <el-input v-model="form.url" placeholder="https://...（可选）" maxlength="500" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="资料描述或学习笔记" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="选择分类" clearable style="width: 100%;">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.resource_type" placeholder="选择类型" clearable style="width: 100%;">
            <el-option v-for="t in types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="标签（逗号分隔）" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.resources-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px;
  min-height: 100vh;
  background: var(--bg-primary);
}

.resources-header h1 {
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

/* ===== AI 搜索 ===== */

.ai-search-section {
  margin-bottom: 20px;
}

.ai-search-input {
  display: flex;
  gap: 8px;
}

.ask-input {
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

.ask-input:focus {
  border-color: var(--accent);
}

.ask-input::placeholder {
  color: var(--text-muted);
}

.ai-answer {
  margin-top: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--accent-bg);
  border-radius: var(--radius-md);
  padding: 14px 16px;
}

.ai-answer-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 6px;
}

.ai-answer-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 8px;
}

/* ===== 筛选栏 ===== */

.filter-bar {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.keyword-input {
  flex: 1;
  min-width: 140px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  padding: 6px 12px;
  outline: none;
  font-family: inherit;
}

.keyword-input:focus {
  border-color: var(--accent);
}

.keyword-input::placeholder {
  color: var(--text-muted);
}

.filter-spacer {
  flex: 1;
}

/* ===== 资料列表 ===== */

.empty {
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
  padding: 60px 0;
}

.resources-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px;
  transition: box-shadow 0.15s;
}

.resource-item:hover {
  box-shadow: var(--shadow);
}

.resource-header-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.resource-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  min-width: 0;
}

.resource-title a {
  color: var(--accent);
  text-decoration: none;
}

.resource-title a:hover {
  text-decoration: underline;
}

.resource-type-badge {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 8px;
  flex-shrink: 0;
}

.resource-desc {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.resource-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.resource-category {
  font-size: 11px;
  background: var(--accent-bg);
  color: var(--accent);
  padding: 2px 8px;
  border-radius: 10px;
}

.tag-chip {
  font-size: 11px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  padding: 2px 8px;
  border-radius: 10px;
}

.resource-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.resource-time {
  flex: 1;
}

.resource-edit {
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 6px;
  height: auto;
}

.resource-edit:hover {
  color: var(--accent);
}

.resource-delete {
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 6px;
  height: auto;
}

.resource-delete:hover {
  color: var(--danger);
}

@media (max-width: 768px) {
  .resources-page {
    padding: 20px 16px;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-spacer {
    display: none;
  }

  .keyword-input {
    min-width: auto;
  }
}
</style>
