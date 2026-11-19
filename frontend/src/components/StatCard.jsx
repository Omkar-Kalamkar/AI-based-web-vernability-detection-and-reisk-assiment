export default function StatCard({ icon: Icon, label, value, sub, tone = 'blue' }) {
  const tones = {
    blue: 'from-electric-500/20 to-electric-600/5 text-electric-300 border-electric-500/25',
    green: 'from-emerald-500/20 to-emerald-600/5 text-emerald-300 border-emerald-500/25',
    red: 'from-red-500/20 to-red-600/5 text-red-300 border-red-500/25',
    orange: 'from-orange-500/20 to-orange-600/5 text-orange-300 border-orange-500/25',
    amber: 'from-amber-500/20 to-amber-600/5 text-amber-300 border-amber-500/25',
    violet: 'from-violet-500/20 to-violet-600/5 text-violet-300 border-violet-500/25',
    slate: 'from-slate-500/20 to-slate-600/5 text-slate-300 border-slate-500/25',
  }
  return (
    <div className="panel panel-hover animate-fade-up p-5">
      <div className={`mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl border bg-gradient-to-br ${tones[tone] || tones.blue}`}>
        <Icon className="h-5 w-5" />
      </div>
      <p className="font-mono text-2xl font-bold tracking-tight text-white">{value}</p>
      <p className="mt-1 text-sm font-medium text-slate-300">{label}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  )
}
