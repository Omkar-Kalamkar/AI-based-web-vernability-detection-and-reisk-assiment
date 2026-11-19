export default function ScoreRing({ score = 100, size = 132, label = 'Security Score', subtitle }) {
  const value = Math.max(0, Math.min(100, Number(score) || 0))
  const stroke = 10
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference
  const color = value >= 80 ? '#22c55e' : value >= 60 ? '#38bdf8' : value >= 40 ? '#f59e0b' : '#ef4444'

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#1d2c4a" strokeWidth={stroke} />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 0.8s ease', filter: `drop-shadow(0 0 6px ${color}55)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-3xl font-bold text-white">{value}</span>
          <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">/ 100</span>
        </div>
      </div>
      {label && <p className="mt-2 text-sm font-semibold text-slate-200">{label}</p>}
      {subtitle && <p className="mt-1 text-center text-xs text-slate-500">{subtitle}</p>}
    </div>
  )
}
