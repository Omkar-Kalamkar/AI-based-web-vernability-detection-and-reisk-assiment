import { apiRequest, setToken } from './api'

export const authService = {
  login: async (email, password) => {
    const data = await apiRequest('/api/auth/login', { method: 'POST', body: { email, password }, auth: false })
    setToken(data.token)
    return data
  },
  register: async (username, email, password) => {
    const data = await apiRequest('/api/auth/register', {
      method: 'POST',
      body: { username, email, password },
      auth: false,
    })
    setToken(data.token)
    return data
  },
  me: () => apiRequest('/api/auth/me'),
  logout: async () => {
    try {
      await apiRequest('/api/auth/logout', { method: 'POST' })
    } finally {
      setToken(null)
    }
  },
}
