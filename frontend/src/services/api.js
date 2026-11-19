const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'
const TOKEN_KEY = 'secureai_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token) => {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function buildUrl(path, params) {
  const url = new URL(`${BASE_URL}${path}`)
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value)
    })
  }
  return url.toString()
}

export async function apiRequest(path, options = {}) {
  const { method = 'GET', body, params, auth = true, signal } = options
  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const token = getToken()
  if (auth && token) headers.Authorization = `Bearer ${token}`

  let response
  try {
    response = await fetch(buildUrl(path, params), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: 'include',
      signal,
    })
  } catch (error) {
    if (error.name !== 'AbortError') {
      throw new Error('Cannot reach the SecureAI backend. Check that it is running on port 5000.')
    }
    throw error
  }

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const message = typeof payload === 'object' ? payload.error || payload.message : payload
    const error = new Error(message || `Request failed with status ${response.status}`)
    error.status = response.status
    if (response.status === 401) {
      setToken(null)
      window.dispatchEvent(new CustomEvent('secureai:unauthorized'))
    }
    throw error
  }
  return payload
}

export async function apiDownload(path, fallbackName, params) {
  const token = getToken()
  const response = await fetch(buildUrl(path, params), {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: 'include',
  })
  if (!response.ok) {
    let message = 'Download failed'
    try {
      const data = await response.json()
      message = data.error || message
    } catch (_) {
      /* non-JSON error */
    }
    throw new Error(message)
  }
  const disposition = response.headers.get('content-disposition') || ''
  const match = disposition.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i)
  const filename = match ? decodeURIComponent(match[1]) : fallbackName
  const blob = await response.blob()
  const objectUrl = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = objectUrl
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  setTimeout(() => URL.revokeObjectURL(objectUrl), 1000)
}

export default apiRequest
