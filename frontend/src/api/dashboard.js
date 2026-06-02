/**
 * 学习面板 API 模块
 *
 * 获取学习统计数据：对话数、消息数、卡片数、活跃天数、每日趋势、热门标签。
 */

import api from './index'

/** 获取学习面板统计数据 */
export function getDashboardStats() {
  return api.get('/dashboard/stats')
}
