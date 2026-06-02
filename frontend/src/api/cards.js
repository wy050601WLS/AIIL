import api from './index'

export function createCard(data) {
  return api.post('/cards', data)
}

export function getCards() {
  return api.get('/cards')
}

export function deleteCard(cardId) {
  return api.delete(`/cards/${cardId}`)
}
