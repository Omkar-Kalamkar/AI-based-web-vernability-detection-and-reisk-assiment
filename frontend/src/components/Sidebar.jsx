import { NavLink, useNavigate } from 'react-router-dom'
import {
  Activity,
  BrainCircuit,
  FileBarChart2,
  Gauge,
  History,
  LogOut,
  Radar,
  Settings,
  ShieldAlert,
} from 'lucide-react'
import Logo from './Logo'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'

const NAV = [
  { to: '/', label: 'Dashboard', icon: Gauge, end: true },
  { to: '/scan', label: 'New Scan', icon: Radar },
  { to: '/vulnerabilities', label: 'Vulnerabilities', icon: ShieldAlert },
  { to: '/ai', label: 'AI Risk Assessment', icon: BrainCircuit },
  { to: '/reports', label: 'Reports', icon: FileBarChart2 },
  { to: '/history', label: 'Scan History', icon: History },
]

export default function Sidebar({ onNavigate }) {
  const { logout, user } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await logout()
      toast.success('You have been signed out')
      navigate('/login')
    } catch (error) {
      toast.error(error.message)
    }
  }

  const linkClass = ({ isActive }) =>
    `group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
      isActive
        ? 'bg-gradient-to-r from-electric-600/25 to-electric-500/5 text-white shadow-inner shadow-electric-500/10 ring-1 ring-inset ring-electric-400/20'
        : 'text-slate-400 hover:bg-white/[0.05] hover:text-white'
    }`

  return (
    <div className="flex h-full flex-col border-r border-white/[0.06] bg-ink-900/95 px-4 py-6 backdrop-blur-xl">
      <div className="px-2" onClick={onNavigate}>
        <NavLink to="/">
          <Logo />
        </NavLink>
      </div>

      <nav className="mt-9 flex-1 space-y-1 overflow-y-auto">
        <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-600">Workspace</p>
        {NAV.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.end} className={linkClass} onClick={onNavigate}>
            <item.icon className="h-[18px] w-[18px] transition group-hover:text-electric-300" />
            <span>{item.label}</span>
          </NavLink>
        ))}
        <p className="mb-3 mt-7 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-600">System</p>
        <NavLink to="/settings" className={linkClass} onClick={onNavigate}>
          <Settings className="h-[18px] w-[18px] transition group-hover:text-electric-300" />
          <span>Settings</span>
        </NavLink>
        <button onClick={handleLogout} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-400 transition hover:bg-red-500/10 hover:text-red-300">
          <LogOut className="h-[18px] w-[18px]" />
          <span>Logout</span>
        </button>
      </nav>

      <div className="mt-6 rounded-xl border border-white/[0.07] bg-gradient-to-br from-electric-600/15 to-transparent p-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-electric-300">
          <Activity className="h-4 w-4" />
          Passive scanning active
        </div>
        <p className="mt-2 text-[11px] leading-relaxed text-slate-400">
          Scope-validated, read-only checks. Authorized targets only.
        </p>
        <div className="mt-3 flex items-center gap-2 border-t border-white/[0.06] pt-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-electric-500/20 text-[11px] font-bold text-electric-200">
            {(user?.username || 'U').slice(0, 1).toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="truncate text-xs font-medium text-slate-200">{user?.username || 'User'}</p>
            <p className="truncate text-[10px] text-slate-500">{user?.email || ''}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
