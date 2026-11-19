import { apiRequest } from './api'

export const aiService = {
  modelInfo: () => apiRequest('/api/ai/model'),
  assessment: (scanId) => apiRequest(`/api/ai/assessment/${scanId}`),
  validation: (scanId) => apiRequest(`/api/ai/validation/${scanId}`),
  explain: (finding) => apiRequest('/api/ai/explain', { method: 'POST', body: finding }),
  scoreGuide: () => apiRequest('/api/ai/score-guide'),
}
