import { apiRequest } from './api'

export const historyService = {
  list: (limit = 100) => apiRequest('/api/history', { params: { limit } }),
  stats: () => apiRequest('/api/history/stats'),
  remove: (id) => apiRequest(`/api/history/${id}`, { method: 'DELETE' }),
  clear: () => apiRequest('/api/history', { method: 'DELETE' }),
}
