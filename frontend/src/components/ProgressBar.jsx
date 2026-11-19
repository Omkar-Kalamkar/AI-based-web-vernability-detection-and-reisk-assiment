export default function ProgressBar({ value = 0, tone = 'blue', className = '' }) {
  const colors = {
    blue: 'from-electric-600 to-electric-400',
    green: 'from-emerald-600 to-emerald-400',
    red: 'from-red-600 to-orange-400',
  }
  return (
    <div className={`h-1.5 w-full overflow-hidden rounded-full bg-white/[0.07] ${className}`}>
      <div
        className={`h-full rounded-full bg-gradient-to-r ${colors[tone] || colors.blue} transition-all duration-500`}
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  )
}
