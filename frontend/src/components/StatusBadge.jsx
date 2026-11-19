const MAP = {
  queued: 'border-slate-500/40 bg-slate-500/10 text-slate-300',
  running: 'border-electric-400/40 bg-electric-500/10 text-electric-300',
  completed: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
  failed: 'border-red-500/40 bg-red-500/10 text-red-300',
  cancelled: 'border-amber-500/40 bg-amber-500/10 text-amber-300',
}

export default function StatusBadge({ status }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold capitalize ${MAP[status] || MAP.queued}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${status === 'running' ? 'animate-pulse bg-electric-400' : 'bg-current'}`} />
      {status}
    </span>
  )
}
