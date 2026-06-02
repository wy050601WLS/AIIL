<script setup>
import { computed, onMounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard'

const store = useDashboardStore()

onMounted(() => store.loadStats())

const statCards = computed(() => {
  if (!store.stats) return []
  return [
    { label: '对话总数', value: store.stats.conversation_count, icon: '💬' },
    { label: '消息总数', value: store.stats.message_count, icon: '📝' },
    { label: '知识卡片', value: store.stats.card_count, icon: '🗂️' },
    { label: '活跃天数', value: store.stats.active_days, icon: '📅' },
  ]
})

const maxCount = computed(() => {
  if (!store.stats) return 1
  return Math.max(1, ...store.stats.daily_messages.map(d => d.count))
})

function barHeight(count) {
  return Math.round((count / maxCount.value) * 100) + '%'
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <h1>学习面板</h1>
      <p class="subtitle">你的学习数据概览</p>
    </div>

    <div v-if="store.loading && !store.stats" class="loading">加载中...</div>

    <template v-else-if="store.stats">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div v-for="card in statCards" :key="card.label" class="stat-card">
          <span class="stat-icon">{{ card.icon }}</span>
          <span class="stat-value">{{ card.value }}</span>
          <span class="stat-label">{{ card.label }}</span>
        </div>
      </div>

      <!-- 每日消息趋势 -->
      <div class="section">
        <h2>最近 30 天消息趋势</h2>
        <div class="chart-area">
          <div class="bar-chart">
            <div
              v-for="day in store.stats.daily_messages"
              :key="day.date"
              class="bar-wrapper"
              :title="`${formatDate(day.date)}: ${day.count} 条`"
            >
              <div class="bar" :style="{ height: barHeight(day.count) }"></div>
            </div>
          </div>
          <div class="chart-labels">
            <span>{{ formatDate(store.stats.daily_messages[0]?.date) }}</span>
            <span>{{ formatDate(store.stats.daily_messages[14]?.date) }}</span>
            <span>{{ formatDate(store.stats.daily_messages[29]?.date) }}</span>
          </div>
        </div>
      </div>

      <!-- 热门标签 -->
      <div v-if="store.stats.top_tags.length > 0" class="section">
        <h2>热门标签</h2>
        <div class="tags-list">
          <span v-for="t in store.stats.top_tags" :key="t.tag" class="tag-item">
            {{ t.tag }}
            <span class="tag-count">{{ t.count }}</span>
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px;
  min-height: 100vh;
  background: var(--bg-primary);
}

.dashboard-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 28px;
}

.loading {
  text-align: center;
  color: var(--text-muted);
  padding: 60px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

.section {
  margin-bottom: 32px;
}

.section h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.chart-area {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 120px;
}

.bar-wrapper {
  flex: 1;
  height: 100%;
  display: flex;
  align-items: flex-end;
  cursor: pointer;
}

.bar {
  width: 100%;
  min-height: 2px;
  background: var(--accent);
  border-radius: 2px 2px 0 0;
  transition: opacity 0.15s;
}

.bar-wrapper:hover .bar {
  opacity: 0.75;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-muted);
}

.tags-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-count {
  background: var(--accent-bg);
  color: var(--accent);
  font-size: 11px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 10px;
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: 20px 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-value {
    font-size: 22px;
  }

  .bar-chart {
    height: 80px;
  }
}
</style>
