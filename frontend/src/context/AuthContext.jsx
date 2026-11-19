import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authService } from '../services/authService'
import { getToken } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    const validate = async () => {
      if (!getToken()) {
        if (active) setLoading(false)
        return
      }
      try {
        const data = await authService.me()
        if (active) setUser(data.user)
      } catch (_) {
        if (active) setUser(null)
      } finally {
        if (active) setLoading(false)
      }
    }
    validate()
    const onUnauthorized = () => {
      setUser(null)
      setLoading(false)
    }
    window.addEventListener('secureai:unauthorized', onUnauthorized)
    return () => {
      active = false
      window.removeEventListener('secureai:unauthorized', onUnauthorized)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await authService.login(email, password)
    setUser(data.user)
    return data.user
  }, [])

  const register = useCallback(async (username, email, password) => {
    const data = await authService.register(username, email, password)
    setUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(async () => {
    await authService.logout()
    setUser(null)
  }, [])

  const value = useMemo(() => ({ user, loading, login, register, logout, isAuthenticated: Boolean(user) }), [user, loading, login, register, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
