<!--
  Resources 视图 — 学习资料与知识库页

  功能：Tab 切换展示学习资料（链接/元数据）和知识库文档（上传文件）
  Tab 1: 学习资料 — AI 搜索、分类/类型筛选、增删改
  Tab 2: 知识库文档 — 上传文件、搜索、查看文档详情
-->
<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useResourcesStore } from '../stores/resources'
import { useKnowledgeStore } from '../stores/knowledge'

const resourcesStore = useResourcesStore()
const knowledgeStore = useKnowledgeStore()
const router = useRouter()

const activeTab = ref('resources')

// ===== 学习资料相关 =====
const filterCategory = ref('')
const filterType = ref('')
const filterKeyword = ref('')
const askQuestion = ref('')

const dialogVisible = ref(false)
const editingId = ref(null)
const form = ref({ title: '', url: '', description: '', category: '', resource_type: '', tags: '', visibility: 'public' })

const categories = ['编程', '数学', '英语', '设计', '科学', '历史', '其他']
const visibilities = [
  { value: 'public', label: '公共', desc: '所有人可见' },
  { value: 'private', label: '私人', desc: '仅自己可见' },
  { value: 'draft', label: '草稿', desc: '仅自己可见，未完成' },
]
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

// ===== 知识库相关 =====
const searchKeyword = ref('')
const uploadDialogVisible = ref(false)
const uploadTitle = ref('')
const uploadTags = ref('')
const uploadVisibility = ref('public')
const selectedFile = ref(null)

const fileTypeIcons = { pdf: '📄', docx: '📝', txt: '📃', md: '📑' }
const fileTypeLabels = { pdf: 'PDF', docx: 'Word', txt: '文本', md: 'Markdown' }

onMounted(() => {
  resourcesStore.loadResources()
  knowledgeStore.loadDocuments()
})

// ===== 学习资料操作 =====
function openAddDialog() {
  editingId.value = null
  form.value = { title: '', url: '', description: '', category: '', resource_type: '', tags: '', visibility: 'public' }
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
    visibility: resource.visibility || 'public',
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
    visibility: form.value.visibility || 'public',
  }
  if (editingId.value) {
    await resourcesStore.editResource(editingId.value, data)
  } else {
    await resourcesStore.addResource(data)
  }
  dialogVisible.value = false
}

async function handleDeleteResource(resource) {
  try {
    await ElMessageBox.confirm('确定删除这条学习资料？', '删除资料', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await resourcesStore.removeResource(resource.id)
  } catch {}
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

// ===== 知识库操作 =====
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
  uploadVisibility.value = 'public'
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
    uploadVisibility.value,
  )
  if (doc) {
    uploadDialogVisible.value = false
  }
}

function goToDetail(id) {
  router.push(`/knowledge/${id}`)
}

async function handleDeleteDoc(doc) {
  try {
    await ElMessageBox.confirm(`确定删除文档「${doc.title}」？`, '删除文档', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await knowledgeStore.removeDocument(doc.id)
  } catch {}
}

// ===== 通用工具 =====
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

function visibilityLabel(v) {
  const found = visibilities.find(item => item.value === v)
  return found ? found.label : v
}

function visibilityClass(v) {
  return `vis-${v || 'public'}`
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}
</script>

<template>
  <div class="resources-page">
    <div class="resources-header">
      <h1>学习资料</h1>
      <p class="subtitle">收集学习资料，上传文档，AI 帮你快速查找</p>
    </div>

    <!-- Tab 切换 -->
    <div class="tab-bar">
      <button class="tab-btn" :class="{ active: activeTab === 'resources' }" @click="activeTab = 'resources'">
        学习资料
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'knowledge' }" @click="activeTab = 'knowledge'">
        知识库文档
      </button>
    </div>

    <!-- ===== Tab 1: 学习资料 ===== -->
    <template v-if="activeTab === 'resources'">
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

      <!-- 资料列表 -->
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
            <span class="visibility-badge" :class="visibilityClass(resource.visibility)">{{ visibilityLabel(resource.visibility) }}</span>
          </div>
          <div v-if="resource.description" class="resource-desc">{{ resource.description }}</div>
          <div class="resource-meta">
            <span v-if="resource.category" class="resource-category">{{ resource.category }}</span>
            <span v-for="tag in tagList(resource.tags)" :key="tag" class="tag-chip">{{ tag }}</span>
          </div>
          <div class="resource-footer">
            <span class="resource-time">{{ formatTime(resource.created_at) }}</span>
            <el-button text size="small" class="resource-edit" @click="openEditDialog(resource)">编辑</el-button>
            <el-button text size="small" class="resource-delete" @click="handleDeleteResource(resource)">删除</el-button>
          </div>
        </div>
      </div>

      <!-- 新增/编辑对话框 -->
      <el-dialog v-model="dialogVisible" :title="editingId ? '编辑资料' : '添加资料'" width="500px" append-to-body>
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
          <el-form-item label="可见性">
            <el-select v-model="form.visibility" style="width: 100%;">
              <el-option v-for="v in visibilities" :key="v.value" :label="v.label" :value="v.value">
                <span>{{ v.label }}</span>
                <span style="color: var(--text-muted); font-size: 12px; margin-left: 8px;">{{ v.desc }}</span>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </template>
      </el-dialog>
    </template>

    <!-- ===== Tab 2: 知识库文档 ===== -->
    <template v-if="activeTab === 'knowledge'">
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

      <div class="resources-grid">
        <div v-for="doc in knowledgeStore.documents" :key="doc.id" class="resource-item doc-clickable" @click="goToDetail(doc.id)">
          <div class="resource-header-row">
            <span class="doc-icon">{{ fileTypeIcons[doc.file_type] || '📄' }}</span>
            <span class="resource-title">{{ doc.title }}</span>
            <span class="resource-type-badge">{{ fileTypeLabels[doc.file_type] || doc.file_type }}</span>
            <span class="visibility-badge" :class="visibilityClass(doc.visibility)">{{ visibilityLabel(doc.visibility) }}</span>
          </div>
          <div v-if="doc.content_text" class="resource-desc doc-preview">{{ doc.content_text.slice(0, 120) }}...</div>
          <div v-if="doc.tags" class="resource-meta">
            <span v-for="tag in tagList(doc.tags)" :key="tag" class="tag-chip">{{ tag }}</span>
          </div>
          <div class="resource-footer">
            <span class="doc-size">{{ formatSize(doc.file_size) }}</span>
            <span class="resource-time">{{ formatTime(doc.created_at) }}</span>
            <el-button text size="small" class="resource-delete" @click.stop="handleDeleteDoc(doc)">删除</el-button>
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
          <el-form-item label="可见性">
            <el-select v-model="uploadVisibility" style="width: 100%;">
              <el-option v-for="v in visibilities" :key="v.value" :label="v.label" :value="v.value">
                <span>{{ v.label }}</span>
                <span style="color: var(--text-muted); font-size: 12px; margin-left: 8px;">{{ v.desc }}</span>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="knowledgeStore.uploading" @click="handleUpload">上传</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<style scoped>
.resources-page {
  max-width: var(--page-max-width);
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
  min-height: 100vh;
  background: var(--bg-primary);
}

.resources-header h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.subtitle {
  font-size: var(--text-base);
  color: var(--text-muted);
  margin-bottom: 20px;
}

/* ===== Tab 切换 ===== */

.tab-bar {
  display: flex;
  gap: var(--space-xs);
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0;
}

.tab-btn {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-muted);
  font-size: var(--text-base);
  font-weight: 500;
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  font-family: inherit;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

/* ===== AI 搜索 ===== */

.ai-search-section {
  margin-bottom: 20px;
}

.ai-search-input {
  display: flex;
  gap: var(--space-sm);
}

.ask-input {
  flex: 1;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-base);
  padding: var(--space-sm) 14px;
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
  margin-top: var(--space-sm);
  background: var(--bg-secondary);
  border: 1px solid var(--accent-bg);
  border-radius: var(--radius-md);
  padding: 14px var(--space-md);
}

.ai-answer-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 6px;
}

.ai-answer-text {
  font-size: var(--text-base);
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: var(--space-sm);
}

/* ===== 筛选栏 ===== */

.filter-bar {
  display: flex;
  gap: var(--space-sm);
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
  font-size: var(--text-sm);
  padding: 6px var(--space-sm);
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

/* ===== 搜索栏（知识库） ===== */

.search-bar {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-base);
  padding: var(--space-sm) 14px;
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

/* ===== 列表通用 ===== */

.empty {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--text-base);
  padding: 60px 0;
}

.resources-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.resource-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  transition: box-shadow 0.15s;
}

.resource-item:hover {
  box-shadow: var(--shadow);
}

.doc-clickable {
  cursor: pointer;
}

.resource-header-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: 6px;
}

.doc-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.resource-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-title a {
  color: var(--accent);
  text-decoration: none;
}

.resource-title a:hover {
  text-decoration: underline;
}

.resource-type-badge {
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px var(--space-sm);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.resource-desc {
  font-size: var(--text-sm);
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: var(--space-sm);
  white-space: pre-wrap;
  word-break: break-word;
}

.doc-preview {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  white-space: normal;
}

.resource-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: var(--space-sm);
}

.resource-category {
  font-size: var(--text-xs);
  background: var(--accent-bg);
  color: var(--accent);
  padding: 2px var(--space-sm);
  border-radius: 10px;
}

.resource-footer {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 12px;
  color: var(--text-muted);
}

.resource-time {
  flex: 1;
}

.doc-size {
  flex-shrink: 0;
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

.file-info {
  margin-top: 6px;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .resources-page {
    padding: 20px 16px;
  }

  .filter-bar,
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-spacer,
  .search-spacer {
    display: none;
  }

  .keyword-input,
  .search-input {
    min-width: auto;
  }
}
</style>
