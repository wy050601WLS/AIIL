<!--
  Cards 视图 — 知识卡片页

  功能：展示知识卡片列表，支持标签筛选、删除
  卡片来源：从 AI 回复中点击「提取卡片」保存
-->
<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useCardsStore } from '../stores/cards'

const cardsStore = useCardsStore()

const filterTag = ref('')  // 当前筛选的标签（空表示全部）

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
        <div class="card-content">{{ card.content }}</div>
        <div v-if="card.tags" class="card-tags">
          <span v-for="tag in tagList(card.tags)" :key="tag" class="tag-chip">{{ tag }}</span>
        </div>
        <div class="card-footer">
          <span v-if="card.source" class="card-source">{{ card.source }}</span>
          <span class="card-time">{{ formatTime(card.created_at) }}</span>
          <el-button text size="small" class="card-delete" @click="handleDelete(card)">删除</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cards-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px;
  min-height: 100vh;
  background: var(--bg-primary);
}

.cards-header h1 {
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

.tag-bar {
  display: flex;
  gap: 4px;
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
  font-size: 14px;
  padding: 60px 0;
}

.cards-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px;
  transition: box-shadow 0.15s;
}

.card-item:hover {
  box-shadow: var(--shadow);
}

.card-content {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 8px;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.tag-chip {
  font-size: 11px;
  background: var(--accent-bg);
  color: var(--accent);
  padding: 2px 8px;
  border-radius: 10px;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.card-source {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

@media (max-width: 768px) {
  .cards-page {
    padding: 20px 16px;
  }
}
</style>
