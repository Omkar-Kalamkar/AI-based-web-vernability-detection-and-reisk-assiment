import { apiRequest } from './api'

export const settingsService = {
  get: () => apiRequest('/api/settings'),
  update: (settings) => apiRequest('/api/settings', { method: 'PUT', body: settings }),
  platform: () => apiRequest('/api/settings/platform'),
}
