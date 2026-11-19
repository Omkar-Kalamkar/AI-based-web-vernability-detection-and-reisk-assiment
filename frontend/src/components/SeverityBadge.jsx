const MAP = {
  critical: { label: 'Critical', className: 'border-red-500/40 bg-red-500/15 text-red-300', dot: 'bg-red-400' },
  high: { label: 'High', className: 'border-orange-500/40 bg-orange-500/15 text-orange-300', dot: 'bg-orange-400' },
  medium: { label: 'Medium', className: 'border-amber-400/40 bg-amber-400/15 text-amber-200', dot: 'bg-amber-300' },
  low: { label: 'Low', className: 'border-sky-500/40 bg-sky-500/15 text-sky-300', dot: 'bg-sky-400' },
  informational: { label: 'Info', className: 'border-slate-500/40 bg-slate-500/15 text-slate-300', dot: 'bg-slate-400' },
}

export const SEVERITY_COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#f59e0b',
  low: '#38bdf8',
  informational: '#94a3b8',
}

export default function SeverityBadge({ severity, size = 'sm' }) {
  const config = MAP[severity] || MAP.informational
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-semibold capitalize ${config.className} ${size === 'lg' ? 'px-3 py-1.5 text-xs' : 'px-2.5 py-1 text-[11px]'}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  )
}
