/**
 * 知识卡片 API 模块
 *
 * 封装知识卡片的创建、查询和删除请求。
 */

import api from './index'

/** 创建知识卡片（content 必填，source 和 tags 可选） */
export function createCard(data) {
  return api.post('/cards', data)
}

/** 获取当前用户的知识卡片列表 */
export function getCards() {
  return api.get('/cards')
}

/** 删除知识卡片 */
export function deleteCard(cardId) {
  return api.delete(`/cards/${cardId}`)
}
