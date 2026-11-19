import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Bell, ChevronDown, Menu, Search, ShieldCheck, X } from 'lucide-react'
import Logo from './Logo'
import { useAuth } from '../hooks/useAuth'

const TITLES = {
  '/': ['Dashboard', 'Security overview and recent activity'],
  '/scan': ['New Scan', 'Run a safe, authorized security assessment'],
  '/vulnerabilities': ['Vulnerabilities', 'Review and manage all detected findings'],
  '/ai': ['AI Risk Assessment', 'Transparent scoring and intelligent explanations'],
  '/reports': ['Reports', 'Export downloadable security reports'],
  '/history': ['Scan History', 'Compare results across previous assessments'],
  '/settings': ['Settings', 'Workspace preferences and platform limits'],
}

export default function Topbar({ onMenuClick }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [search, setSearch] = useState('')
  const [openMenu, setOpenMenu] = useState(null)
  const [title, subtitle] = TITLES[location.pathname] || ['SecureAI', 'Security intelligence workspace']

  useEffect(() => {
    setOpenMenu(null)
    setSearch('')
  }, [location.pathname])

  const submitSearch = (event) => {
    event.preventDefault()
    if (search.trim()) navigate(`/vulnerabilities?search=${encodeURIComponent(search.trim())}`)
  }

  return (
    <header className="sticky top-0 z-30 border-b border-white/[0.06] bg-ink-950/80 px-4 py-4 backdrop-blur-xl sm:px-6">
      <div className="flex items-center gap-3">
        <button onClick={onMenuClick} className="rounded-xl border border-white/10 p-2 text-slate-300 transition hover:bg-white/5 lg:hidden" aria-label="Open navigation">
          <Menu className="h-5 w-5" />
        </button>
        <div className="lg:hidden">
          <Logo compact />
        </div>

        <div className="hidden min-w-0 lg:block">
          <h1 className="font-display text-xl font-semibold tracking-tight text-white">{title}</h1>
          <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>
        </div>

        <form onSubmit={submitSearch} className="ml-auto hidden w-full max-w-xs md:block">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search vulnerabilities..."
              className="field py-2.5 pl-10 pr-3 text-xs"
            />
          </div>
        </form>

        <div className="relative ml-auto md:ml-0">
          <button
            onClick={() => setOpenMenu(openMenu === 'notifications' ? null : 'notifications')}
            className="relative rounded-xl border border-white/10 bg-white/[0.03] p-2.5 text-slate-300 transition hover:text-white"
            aria-label="Notifications"
          >
            <Bell className="h-4 w-4" />
            <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-electric-400" />
          </button>
          {openMenu === 'notifications' && (
            <div className="absolute right-0 top-12 z-50 w-72 rounded-xl border border-white/10 bg-ink-850 p-4 shadow-2xl">
              <p className="text-sm font-semibold text-white">Security feed</p>
              <div className="mt-3 space-y-3 text-xs text-slate-400">
                <p className="flex gap-2"><ShieldCheck className="h-4 w-4 shrink-0 text-emerald-400" /> Scans are non-destructive and scope-validated.</p>
                <p className="flex gap-2"><ShieldCheck className="h-4 w-4 shrink-0 text-emerald-400" /> Potential indicators are separated from confirmed findings.</p>
                <p className="flex gap-2"><ShieldCheck className="h-4 w-4 shrink-0 text-emerald-400" /> Only localhost lab targets are enabled by default.</p>
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setOpenMenu(openMenu === 'user' ? null : 'user')}
            className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] py-1.5 pl-1.5 pr-2.5 transition hover:bg-white/[0.07]"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-electric-500 to-electric-700 text-xs font-bold text-white">
              {(user?.username || 'U').slice(0, 1).toUpperCase()}
            </div>
            <span className="hidden text-sm font-medium text-slate-200 sm:block">{user?.username || 'User'}</span>
            <ChevronDown className="h-3.5 w-3.5 text-slate-500" />
          </button>
          {openMenu === 'user' && (
            <div className="absolute right-0 top-12 z-50 w-56 rounded-xl border border-white/10 bg-ink-850 p-2 shadow-2xl">
              <div className="border-b border-white/[0.07] px-3 py-2">
                <p className="truncate text-sm font-semibold text-white">{user?.username}</p>
                <p className="truncate text-xs text-slate-500">{user?.email}</p>
              </div>
              <button onClick={() => navigate('/settings')} className="mt-1 w-full rounded-lg px-3 py-2 text-left text-sm text-slate-300 hover:bg-white/5 hover:text-white">
                Settings
              </button>
              <button
                onClick={async () => {
                  try {
                    await logout()
                    navigate('/login')
                  } catch (_) {
                    /* handled by navigation */
                  }
                }}
                className="w-full rounded-lg px-3 py-2 text-left text-sm text-red-300 hover:bg-red-500/10"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
      {location.pathname !== '/' && (
        <div className="mt-2 lg:hidden">
          <h1 className="font-display text-lg font-semibold text-white">{title}</h1>
          <p className="text-[11px] text-slate-500">{subtitle}</p>
        </div>
      )}
      {openMenu && (
        <button className="fixed inset-0 z-[-1]" onClick={() => setOpenMenu(null)} aria-label="Close menu">
          <X className="sr-only" />
        </button>
      )}
    </header>
  )
}
