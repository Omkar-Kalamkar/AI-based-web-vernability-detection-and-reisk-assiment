import { ShieldCheck } from 'lucide-react'

export default function Logo({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-electric-500 to-electric-700 shadow-lg shadow-electric-600/30">
        <ShieldCheck className="h-5 w-5 text-white" strokeWidth={2.2} />
        <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full border-2 border-ink-900 bg-success" />
      </div>
      {!compact && (
        <div className="leading-tight">
          <p className="font-display text-lg font-bold tracking-tight text-white">Secure<span className="text-electric-400">AI</span></p>
          <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-slate-500">Security Intelligence</p>
        </div>
      )}
    </div>
  )
}
