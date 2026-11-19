import { apiRequest } from './api'

export const scanService = {
  create: (targetUrl) =>
    apiRequest('/api/scans', {
      method: 'POST',
      body: { target_url: targetUrl, authorization_confirmed: true },
    }),
  list: (limit = 50) => apiRequest('/api/scans', { params: { limit } }),
  get: (id) => apiRequest(`/api/scans/${id}`),
  remove: (id) => apiRequest(`/api/scans/${id}`, { method: 'DELETE' }),
  retry: (id) => apiRequest(`/api/scans/${id}/retry`, { method: 'POST' }),
}
