import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { SEVERITY_COLORS } from './SeverityBadge'
import EmptyState from './EmptyState'

const tooltipStyle = {
  backgroundColor: '#0c1528',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '10px',
  color: '#e2e8f0',
  fontSize: '12px',
  boxShadow: '0 18px 45px -20px rgba(0,0,0,0.9)',
}

const axisStyle = { fill: '#64748b', fontSize: 11 }

export function SeverityPie({ data = [] }) {
  const filtered = data.filter((item) => item.value > 0)
  if (!filtered.length) return <EmptyState icon={PieChart} title="No findings yet" description="Run a scan to see the severity distribution." />
  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={filtered} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={58} outerRadius={94} paddingAngle={3} stroke="none">
          {filtered.map((item) => (
            <Cell key={item.name} fill={SEVERITY_COLORS[item.name.toLowerCase()] || '#64748b'} />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} />
        <Legend iconType="circle" wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function ScoreTrendChart({ data = [] }) {
  if (!data.length) return <EmptyState icon={AreaChart} title="No completed scans" description="Score history appears here after a scan finishes." />
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ top: 10, right: 8, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.45} />
            <stop offset="100%" stopColor="#2563eb" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" vertical={false} />
        <XAxis dataKey="date" tick={axisStyle} axisLine={false} tickLine={false} />
        <YAxis domain={[0, 100]} tick={axisStyle} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={tooltipStyle} />
        <Area type="monotone" dataKey="score" name="Security score" stroke="#38bdf8" strokeWidth={2.5} fill="url(#scoreFill)" dot={{ r: 3, fill: '#0ea5e9' }} />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export function ActivityChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 10, right: 8, left: -24, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" vertical={false} />
        <XAxis dataKey="date" tick={axisStyle} axisLine={false} tickLine={false} interval={2} />
        <YAxis allowDecimals={false} tick={axisStyle} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={tooltipStyle} cursor={{ fill: 'rgba(56,189,248,0.07)' }} />
        <Bar dataKey="scans" name="Scans" fill="#2563eb" radius={[5, 5, 0, 0]} maxBarSize={22} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function CategoryBars({ data = [] }) {
  const sorted = [...data].sort((a, b) => b.value - a.value).slice(0, 7)
  if (!sorted.length) return <EmptyState icon={BarChart} title="No categories yet" description="Finding categories will appear after a scan." />
  return (
    <div className="space-y-3">
      {sorted.map((item, index) => (
        <div key={item.name}>
          <div className="mb-1.5 flex items-center justify-between text-xs">
            <span className="truncate pr-3 text-slate-300">{item.name}</span>
            <span className="font-mono font-semibold text-white">{item.value}</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className="h-full rounded-full bg-gradient-to-r from-electric-700 to-electric-400"
              style={{ width: `${Math.max(6, (item.value / sorted[0].value) * 100)}%`, opacity: 1 - index * 0.08 }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
