import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'
import { AlertTriangle, CheckCircle2, Info, X, XCircle } from 'lucide-react'

const ToastContext = createContext(null)

const STYLES = {
  success: { icon: CheckCircle2, accent: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' },
  error: { icon: XCircle, accent: 'border-red-500/40 bg-red-500/10 text-red-300' },
  warning: { icon: AlertTriangle, accent: 'border-amber-500/40 bg-amber-500/10 text-amber-300' },
  info: { icon: Info, accent: 'border-sky-500/40 bg-sky-500/10 text-sky-300' },
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const counter = useRef(0)

  const dismiss = useCallback((id) => setToasts((items) => items.filter((item) => item.id !== id)), [])

  const push = useCallback(
    (message, type = 'info', title = '') => {
      const id = ++counter.current
      setToasts((items) => [...items, { id, message, type, title }])
      setTimeout(() => dismiss(id), 5000)
    },
    [dismiss],
  )

  const value = useMemo(
    () => ({
      toast: push,
      success: (message, title) => push(message, 'success', title),
      error: (message, title) => push(message, 'error', title),
      warning: (message, title) => push(message, 'warning', title),
      info: (message, title) => push(message, 'info', title),
      dismiss,
    }),
    [push, dismiss],
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed bottom-5 right-5 z-[100] flex w-[min(92vw,380px)] flex-col gap-3">
        {toasts.map((item) => {
          const style = STYLES[item.type] || STYLES.info
          const Icon = style.icon
          return (
            <div
              key={item.id}
              className={`pointer-events-auto flex items-start gap-3 rounded-xl border ${style.accent} bg-ink-850/95 p-4 shadow-2xl backdrop-blur-xl animate-fade-up`}
            >
              <Icon className="mt-0.5 h-5 w-5 shrink-0" />
              <div className="min-w-0 flex-1">
                {item.title && <p className="text-sm font-semibold text-white">{item.title}</p>}
                <p className="text-sm leading-relaxed text-slate-300">{item.message}</p>
              </div>
              <button onClick={() => dismiss(item.id)} className="text-slate-500 transition hover:text-white" aria-label="Dismiss notification">
                <X className="h-4 w-4" />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast must be used inside ToastProvider')
  return context
}
