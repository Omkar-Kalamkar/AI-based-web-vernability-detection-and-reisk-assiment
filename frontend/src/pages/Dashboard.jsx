import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertOctagon, ArrowUpRight, Download, FileWarning, Radar, ShieldCheck, TriangleAlert } from 'lucide-react'
import StatCard from '../components/StatCard'
import ScoreRing from '../components/ScoreRing'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import Loader from '../components/Loader'
import { ActivityChart, ScoreTrendChart, SeverityPie } from '../components/Charts'
import { historyService } from '../services/historyService'
import { reportService } from '../services/reportService'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import { usePolling } from '../hooks/usePolling'

export default function Dashboard() {
  const { user } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      const result = await historyService.stats()
      setData(result)
      setError('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  usePolling(load, 8000, !loading)

  useEffect(() => {
    load()
  }, [load])

  if (loading) return <Loader label="Loading dashboard..." />
  if (error && !data) {
    return <EmptyState title="Could not load dashboard" description={error} action={<button onClick={load} className="btn-primary">Retry</button>} />
  }

  const stats = data?.stats || {}
  const recent = data?.recent_scans || []

  const download = async (scanId) => {
    try {
      await reportService.downloadPdf(scanId)
      toast.success('PDF report downloaded')
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="panel relative overflow-hidden p-6">
        <div className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-electric-500/15 blur-3xl" />
        <div className="relative flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-electric-300">Security workspace</p>
            <h2 className="mt-2 font-display text-2xl font-bold text-white sm:text-3xl">Welcome back, {user?.username || 'analyst'}</h2>
            <p className="muted mt-2">Monitor your security posture and act on the highest risks first.</p>
          </div>
          <Link to="/scan" className="btn-primary">Start scan <ArrowUpRight className="h-4 w-4" /></Link>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4 xl:grid-cols-7">
        <StatCard icon={Radar} label="Total scans" value={stats.total_scans ?? 0} sub={`${stats.completed_scans ?? 0} completed`} tone="blue" />
        <StatCard icon={FileWarning} label="Total findings" value={stats.total_vulnerabilities ?? 0} tone="violet" />
        <StatCard icon={AlertOctagon} label="Critical" value={stats.critical ?? 0} tone="red" />
        <StatCard icon={TriangleAlert} label="High risk" value={stats.high ?? 0} tone="orange" />
        <StatCard icon={TriangleAlert} label="Medium" value={stats.medium ?? 0} tone="amber" />
        <StatCard icon={ShieldCheck} label="Low / Info" value={(stats.low ?? 0) + (stats.informational ?? 0)} tone="green" />
        <StatCard icon={ShieldCheck} label="Avg. security score" value={`${stats.average_score ?? 100}`} sub="out of 100" tone="green" />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="panel p-5">
          <h3 className="section-title">Vulnerability distribution</h3>
          <p className="muted mt-1 text-xs">All findings across completed scans</p>
          <div className="mt-3"><SeverityPie data={data?.severity_distribution || []} /></div>
        </div>
        <div className="panel p-5 xl:col-span-2">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="section-title">Security score trend</h3>
              <p className="muted mt-1 text-xs">Higher is better — compare before and after remediation</p>
            </div>
            <div className="flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-3 py-2">
              <ScoreRing score={stats.latest_score ?? stats.average_score ?? 100} size={52} label="" />
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">Latest score</p>
                <p className="font-mono text-lg font-bold text-white">{stats.latest_score ?? '--'}</p>
              </div>
            </div>
          </div>
          <div className="mt-4"><ScoreTrendChart data={data?.score_trend || []} /></div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="panel p-5 xl:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="section-title">Recent scans</h3>
              <p className="muted mt-1 text-xs">Latest assessments and their outcomes</p>
            </div>
            <Link to="/history" className="text-xs font-semibold text-electric-400 hover:text-electric-300">View all</Link>
          </div>
          {recent.length === 0 ? (
            <div className="mt-5">
              <EmptyState
                icon={Radar}
                title="No scans yet"
                description="Start your first authorized scan to populate the dashboard."
                action={<Link to="/scan" className="btn-primary">Create a scan</Link>}
              />
            </div>
          ) : (
            <div className="mt-5 overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead>
                  <tr className="border-b border-white/[0.07] text-[11px] uppercase tracking-wider text-slate-500">
                    <th className="pb-3 font-medium">Target</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3 font-medium">Score</th>
                    <th className="pb-3 font-medium">Findings</th>
                    <th className="pb-3 font-medium">Date</th>
                    <th className="pb-3 text-right font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.05]">
                  {recent.map((scan) => (
                    <tr key={scan.id} className="transition hover:bg-white/[0.02]">
                      <td className="py-3.5">
                        <p className="max-w-[220px] truncate font-medium text-slate-200">{scan.target_host}</p>
                        <p className="font-mono text-[10px] text-slate-500">{scan.id.slice(0, 14)}</p>
                      </td>
                      <td className="py-3.5"><StatusBadge status={scan.status} /></td>
                      <td className="py-3.5 font-mono font-semibold text-white">{scan.security_score}</td>
                      <td className="py-3.5 text-slate-300">{scan.total_findings}</td>
                      <td className="py-3.5 text-xs text-slate-500">{scan.created_at ? new Date(scan.created_at).toLocaleDateString() : '-'}</td>
                      <td className="py-3.5">
                        <div className="flex justify-end gap-2">
                          <button onClick={() => navigate(`/scan?scan=${scan.id}`)} className="btn-ghost px-2.5 py-1.5 text-xs">View</button>
                          {scan.status === 'completed' && (
                            <button onClick={() => download(scan.id)} className="btn-ghost px-2.5 py-1.5 text-xs" title="Download PDF">
                              <Download className="h-3.5 w-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="panel p-5">
          <h3 className="section-title">Scan activity</h3>
          <p className="muted mt-1 text-xs">Scans started in the last 14 days</p>
          <div className="mt-5"><ActivityChart data={data?.activity || []} /></div>
        </div>
      </div>
    </div>
  )
}
