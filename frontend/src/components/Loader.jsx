export default function Loader({ label = 'Loading', size = 'md' }) {
  const dimension = size === 'sm' ? 'h-4 w-4' : 'h-7 w-7'
  return (
    <div className="flex items-center justify-center gap-3 py-10">
      <span className={`${dimension} animate-spin rounded-full border-2 border-electric-500/25 border-t-electric-400`} />
      {label && <span className="text-sm text-slate-400">{label}</span>}
    </div>
  )
}

export function PageLoader() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Loader label="Loading SecureAI workspace..." />
    </div>
  )
}
