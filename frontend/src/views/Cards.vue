<!--
  Cards 视图 — 知识卡片页

  功能：展示知识卡片列表，支持标签筛选、编辑、删除
  卡片来源：从 AI 回复中点击「提取卡片」保存
-->
<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useCardsStore } from '../stores/cards'

const cardsStore = useCardsStore()

const filterTag = ref('')  // 当前筛选的标签（空表示全部）

// 编辑状态
const editingId = ref(null)    // 正在编辑的卡片 ID
const editContent = ref('')    // 编辑中的内容
const editTags = ref('')       // 编辑中的标签

/** 根据标签关键词过滤卡片列表 */
const filteredCards = computed(() => {
  if (!filterTag.value.trim()) return cardsStore.cards
  const q = filterTag.value.toLowerCase()
  return cardsStore.cards.filter(c =>
    (c.tags || '').toLowerCase().includes(q) || c.content.toLowerCase().includes(q)
  )
})

/** 提取所有卡片中的不重复标签（用于标签筛选栏） */
const allTags = computed(() => {
  const set = new Set()
  for (const c of cardsStore.cards) {
    if (c.tags) {
      c.tags.split(',').map(t => t.trim()).filter(Boolean).forEach(t => set.add(t))
    }
  }
  return [...set]
})

onMounted(() => cardsStore.loadCards())

/** 开始编辑卡片 */
function startEdit(card) {
  editingId.value = card.id
  editContent.value = card.content
  editTags.value = card.tags || ''
}

/** 取消编辑 */
function cancelEdit() {
  editingId.value = null
}

/** 保存编辑 */
async function saveEdit(card) {
  const content = editContent.value.trim()
  if (!content) return
  await cardsStore.editCard(card.id, { content, tags: editTags.value.trim() || null })
  editingId.value = null
}

/** 删除卡片（带确认弹窗） */
async function handleDelete(card) {
  try {
    await ElMessageBox.confirm('确定删除这条知识卡片？', '删除卡片', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await cardsStore.removeCard(card.id)
  } catch {
    // 用户取消删除
  }
}

/** 格式化时间为 M/D HH:MM */
function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

/** 将逗号分隔的标签字符串拆分为数组 */
function tagList(tags) {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}
</script>

<template>
  <div class="cards-page">
    <div class="cards-header">
      <h1>知识卡片</h1>
      <p class="subtitle">收藏 AI 回复中的精华内容，随时回顾</p>
    </div>

    <div v-if="allTags.length > 0" class="tag-bar">
      <el-button
        text
        size="small"
        :class="{ 'tag-active': !filterTag }"
        @click="filterTag = ''"
      >全部</el-button>
      <el-button
        v-for="tag in allTags"
        :key="tag"
        text
        size="small"
        :class="{ 'tag-active': filterTag === tag }"
        @click="filterTag = tag"
      >{{ tag }}</el-button>
    </div>

    <div v-if="cardsStore.loading && cardsStore.cards.length === 0" class="empty">
      加载中...
    </div>
    <div v-else-if="filteredCards.length === 0" class="empty">
      {{ filterTag ? '没有匹配的卡片' : '还没有知识卡片，在对话中点击「提取卡片」保存' }}
    </div>

    <div class="cards-grid">
      <div v-for="card in filteredCards" :key="card.id" class="card-item">
        <!-- 编辑模式 -->
        <template v-if="editingId === card.id">
          <textarea
            v-model="editContent"
            class="edit-textarea"
            rows="4"
            placeholder="卡片内容"
          ></textarea>
          <input
            v-model="editTags"
            class="edit-tags-input"
            placeholder="标签（逗号分隔）"
          />
          <div class="edit-actions">
            <el-button type="primary" size="small" @click="saveEdit(card)">保存</el-button>
            <el-button size="small" @click="cancelEdit">取消</el-button>
          </div>
        </template>
        <!-- 展示模式 -->
        <template v-else>
          <div class="card-content">{{ card.content }}</div>
          <div v-if="card.tags" class="card-tags">
            <span v-for="tag in tagList(card.tags)" :key="tag" class="tag-chip tag-chip--accent">{{ tag }}</span>
          </div>
          <div class="card-footer">
            <span v-if="card.source" class="card-source">{{ card.source }}</span>
            <span class="card-time">{{ formatTime(card.created_at) }}</span>
            <el-button text size="small" class="card-edit" @click="startEdit(card)">编辑</el-button>
            <el-button text size="small" class="card-delete" @click="handleDelete(card)">删除</el-button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cards-page {
  max-width: var(--page-max-width);
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
  min-height: 100vh;
  background: var(--bg-primary);
}

.cards-header h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.subtitle {
  font-size: var(--text-base);
  color: var(--text-muted);
  margin-bottom: var(--space-lg);
}

.tag-bar {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.tag-active {
  color: var(--accent) !important;
  font-weight: 600;
}

.empty {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--text-base);
  padding: 60px 0;
}

.cards-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.card-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  transition: box-shadow 0.15s;
}

.card-item:hover {
  box-shadow: var(--shadow);
}

.card-content {
  font-size: var(--text-base);
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: var(--space-sm);
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: var(--space-sm);
}

.card-footer {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 12px;
  color: var(--text-muted);
}

.card-source {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-edit {
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 6px;
  height: auto;
}

.card-edit:hover {
  color: var(--accent);
}

.card-delete {
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 6px;
  height: auto;
}

.card-delete:hover {
  color: var(--danger);
}

.edit-textarea {
  width: 100%;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-base);
  line-height: 1.7;
  padding: var(--space-sm) var(--space-sm);
  resize: vertical;
  outline: none;
  font-family: inherit;
  margin-bottom: var(--space-sm);
}

.edit-textarea:focus {
  border-color: var(--accent);
}

.edit-tags-input {
  width: 100%;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-sm);
  padding: 6px var(--space-sm);
  outline: none;
  margin-bottom: var(--space-sm);
}

.edit-tags-input:focus {
  border-color: var(--accent);
}

.edit-actions {
  display: flex;
  gap: var(--space-sm);
}

@media (max-width: 768px) {
  .cards-page {
    padding: 20px 16px;
  }
}
</style>
