import { AlertTriangle } from 'lucide-react'
import Modal from './Modal'

export default function ConfirmDialog({ open, onClose, onConfirm, title, message, confirmLabel = 'Confirm', danger = false, busy = false }) {
  return (
    <Modal open={open} onClose={onClose} title={title} width="max-w-md">
      <div className="flex gap-4">
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${danger ? 'bg-red-500/15 text-red-300' : 'bg-electric-500/15 text-electric-300'}`}>
          <AlertTriangle className="h-5 w-5" />
        </div>
        <p className="text-sm leading-relaxed text-slate-300">{message}</p>
      </div>
      <div className="mt-6 flex justify-end gap-3">
        <button onClick={onClose} className="btn-ghost" disabled={busy}>Cancel</button>
        <button onClick={onConfirm} className={danger ? 'btn-danger' : 'btn-primary'} disabled={busy}>
          {busy ? 'Working...' : confirmLabel}
        </button>
      </div>
    </Modal>
  )
}
