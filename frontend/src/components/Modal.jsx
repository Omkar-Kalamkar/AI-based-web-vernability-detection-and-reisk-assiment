import { useEffect } from 'react'
import { X } from 'lucide-react'

export default function Modal({ open, onClose, title, description, children, width = 'max-w-2xl' }) {
  useEffect(() => {
    if (!open) return undefined
    const onKey = (event) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ink-950/85 p-4 backdrop-blur-sm" onMouseDown={onClose}>
      <div
        className={`w-full ${width} animate-fade-up rounded-2xl border border-white/10 bg-ink-850 shadow-2xl`}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-white/[0.07] p-5">
          <div>
            <h2 className="font-display text-lg font-semibold text-white">{title}</h2>
            {description && <p className="muted mt-1">{description}</p>}
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-slate-400 transition hover:bg-white/10 hover:text-white" aria-label="Close dialog">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="max-h-[72vh] overflow-y-auto p-5">{children}</div>
      </div>
    </div>
  )
}
