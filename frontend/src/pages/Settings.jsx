import { useEffect, useState } from 'react'
import { CheckCircle2, Database, Save, Server, Settings2, ShieldCheck, Wifi } from 'lucide-react'
import { settingsService } from '../services/settingsService'
import { apiRequest } from '../services/api'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import Loader from '../components/Loader'

export default function Settings() {
  const toast = useToast()
  const { user } = useAuth()
  const [settings, setSettings] = useState(null)
  const [platform, setPlatform] = useState(null)
  const [busy, setBusy] = useState(false)
  const [connection, setConnection] = useState(null)

  useEffect(() => {
    Promise.all([settingsService.get(), settingsService.platform()])
      .then(([a, b]) => {
        setSettings(a.settings)
        setPlatform(b.platform)
      })
      .catch((error) => toast.error(error.message))
  }, [])

  const save = async (event) => {
    event.preventDefault()
    setBusy(true)
    try {
      const result = await settingsService.update(settings)
      setSettings(result.settings)
      toast.success('Settings saved')
    } catch (error) {
      toast.error(error.message)
    } finally {
      setBusy(false)
    }
  }

  const verify = async () => {
    try {
      const data = await apiRequest('/api/health', { auth: false })
      setConnection(data)
      toast.success('Backend connection verified')
    } catch (error) {
      setConnection({ error: error.message })
      toast.error(error.message)
    }
  }

  if (!settings) return <Loader label="Loading settings..." />

  return (
    <div className="space-y-6">
      <form onSubmit={save} className="grid gap-6 xl:grid-cols-2">
        <div className="panel p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-electric-500/25 bg-electric-500/10 text-electric-300"><Settings2 className="h-5 w-5" /></div>
            <div>
              <h2 className="section-title">Workspace preferences</h2>
              <p className="muted text-xs">These preferences apply to your account.</p>
            </div>
          </div>
          <div className="mt-6 space-y-5">
            <div>
              <label className="label">Interface theme</label>
              <select value={settings.theme} onChange={(event) => setSettings({ ...settings, theme: event.target.value })} className="field">
                <option value="dark">Dark (recommended)</option>
                <option value="light">Light</option>
              </select>
            </div>
            <div>
              <label className="label">Risk sensitivity</label>
              <select value={settings.risk_sensitivity} onChange={(event) => setSettings({ ...settings, risk_sensitivity: event.target.value })} className="field">
                <option value="conservative">Conservative — fewer, higher-confidence findings</option>
                <option value="balanced">Balanced — recommended</option>
                <option value="aggressive">Aggressive — include potential indicators</option>
              </select>
            </div>
            <div>
              <label className="label">Default pages per scan</label>
              <input type="number" min={1} max={20} value={settings.default_max_pages} onChange={(event) => setSettings({ ...settings, default_max_pages: Number(event.target.value) })} className="field font-mono" />
            </div>
            <label className="flex items-center justify-between rounded-xl border border-white/[0.07] bg-white/[0.02] p-4">
              <span>
                <span className="block text-sm font-medium text-slate-200">Desktop notifications</span>
                <span className="block text-xs text-slate-500">Show alerts when scans finish.</span>
              </span>
              <input type="checkbox" checked={settings.notifications} onChange={(event) => setSettings({ ...settings, notifications: event.target.checked })} className="h-4 w-4 accent-electric-500" />
            </label>
            <label className="flex items-center justify-between rounded-xl border border-white/[0.07] bg-white/[0.02] p-4">
              <span>
                <span className="block text-sm font-medium text-slate-200">Auto-refresh dashboards</span>
                <span className="block text-xs text-slate-500">Poll for scan progress automatically.</span>
              </span>
              <input type="checkbox" checked={settings.auto_refresh} onChange={(event) => setSettings({ ...settings, auto_refresh: event.target.checked })} className="h-4 w-4 accent-electric-500" />
            </label>
            <button type="submit" className="btn-primary w-full" disabled={busy}><Save className="h-4 w-4" /> {busy ? 'Saving...' : 'Save preferences'}</button>
          </div>
        </div>

        <div className="space-y-6">
          <div className="panel p-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-emerald-500/25 bg-emerald-500/10 text-emerald-300"><ShieldCheck className="h-5 w-5" /></div>
              <div>
                <h2 className="section-title">Account</h2>
                <p className="muted text-xs">Your SecureAI session details.</p>
              </div>
            </div>
            <div className="mt-5 space-y-3 text-sm">
              <div className="flex justify-between gap-4 rounded-xl border border-white/[0.07] bg-white/[0.02] p-3"><span className="text-slate-500">Username</span><span className="font-medium text-slate-200">{user?.username}</span></div>
              <div className="flex justify-between gap-4 rounded-xl border border-white/[0.07] bg-white/[0.02] p-3"><span className="text-slate-500">Email</span><span className="truncate font-medium text-slate-200">{user?.email}</span></div>
              <div className="flex justify-between gap-4 rounded-xl border border-white/[0.07] bg-white/[0.02] p-3"><span className="text-slate-500">Member since</span><span className="font-medium text-slate-200">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</span></div>
            </div>
          </div>

          <div className="panel p-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-electric-500/25 bg-electric-500/10 text-electric-300"><Server className="h-5 w-5" /></div>
              <div>
                <h2 className="section-title">Platform scan policy</h2>
                <p className="muted text-xs">Configured by the administrator via environment variables.</p>
              </div>
            </div>
            {platform ? (
              <div className="mt-5 grid gap-3 text-xs sm:grid-cols-2">
                {[
                  ['Local lab mode', platform.local_lab_mode ? 'Enabled' : 'Disabled'],
                  ['External targets', platform.external_targets_allowed ? 'Allowed' : 'Blocked'],
                  ['Connect timeout', `${platform.scan_connect_timeout}s`],
                  ['Read timeout', `${platform.scan_read_timeout}s`],
                  ['Max pages', platform.max_pages_per_scan],
                  ['Rate limit', `${platform.scan_rate_limit_per_hour}/hour`],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
                    <p className="text-slate-500">{label}</p>
                    <p className="mt-1 font-mono font-semibold text-slate-200">{value}</p>
                  </div>
                ))}
                <div className="sm:col-span-2 rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
                  <p className="text-slate-500">Allowed lab hosts</p>
                  <p className="mt-1 font-mono text-slate-300">{platform.allowed_lab_hosts.join(', ')}</p>
                  <p className="mt-2 text-slate-500">Allowed ports</p>
                  <p className="mt-1 font-mono text-slate-300">{platform.allowed_lab_ports.join(', ')}</p>
                </div>
              </div>
            ) : (
              <Loader label="Loading platform policy..." size="sm" />
            )}
          </div>

          <div className="panel p-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-violet-500/25 bg-violet-500/10 text-violet-300"><Database className="h-5 w-5" /></div>
              <div>
                <h2 className="section-title">Backend connection</h2>
                <p className="muted text-xs">Verify the REST API is reachable.</p>
              </div>
            </div>
            <button onClick={verify} className="btn-ghost mt-5 w-full"><Wifi className="h-4 w-4" /> Verify connection</button>
            {connection && (
              <div className={`mt-4 flex items-start gap-2 rounded-xl border p-3 text-xs ${connection.error ? 'border-red-500/25 bg-red-500/10 text-red-300' : 'border-emerald-500/25 bg-emerald-500/10 text-emerald-300'}`}>
                {connection.error ? <Wifi className="mt-0.5 h-4 w-4" /> : <CheckCircle2 className="mt-0.5 h-4 w-4" />}
                {connection.error || `${connection.service} API is healthy (lab mode: ${connection.lab_mode})`}
              </div>
            )}
          </div>
        </div>
      </form>
    </div>
  )
}
