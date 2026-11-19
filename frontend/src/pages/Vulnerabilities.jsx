import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Filter, Search, ShieldAlert } from 'lucide-react'
import SeverityBadge from '../components/SeverityBadge'
import Modal from '../components/Modal'
import FindingDetails from '../components/FindingDetails'
import EmptyState from '../components/EmptyState'
import Loader from '../components/Loader'
import { vulnerabilityService } from '../services/vulnerabilityService'
import { useToast } from '../hooks/useToast'

const STATUS_OPTIONS = ['all', 'open', 'in_progress', 'resolved', 'false_positive', 'accepted']

export default function Vulnerabilities() {
  const toast = useToast()
  const [searchParams] = useSearchParams()
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [severity, setSeverity] = useState('all')
  const [status, setStatus] = useState('all')
  const [items, setItems] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [list, summaryData] = await Promise.all([
        vulnerabilityService.list({ search, severity, status, limit: 500 }),
        vulnerabilityService.summary(),
      ])
      setItems(list.vulnerabilities)
      setSummary(summaryData)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }, [search, severity, status])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    const value = searchParams.get('search')
    if (value !== null) setSearch(value)
  }, [searchParams])

  const updateStatus = async (findingId, nextStatus) => {
    try {
      const result = await vulnerabilityService.updateStatus(findingId, nextStatus)
      setItems((current) => current.map((item) => (item.id === findingId ? result.vulnerability : item)))
      setSelected((current) => (current?.id === findingId ? result.vulnerability : current))
      toast.success(`Status updated to ${nextStatus.replace('_', ' ')}`)
    } catch (error) {
      toast.error(error.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          ['All findings', summary?.total ?? 0, 'blue'],
          ['Open', summary?.open_count ?? 0, 'violet'],
          ['Critical + High', (summary?.by_severity?.critical || 0) + (summary?.by_severity?.high || 0), 'red'],
          ['Potential indicators', items.filter((item) => !item.verified).length, 'amber'],
        ].map(([label, value, tone]) => (
          <div key={label} className="panel p-5">
            <p className={`font-mono text-2xl font-bold ${tone === 'red' ? 'text-red-300' : tone === 'amber' ? 'text-amber-300' : 'text-white'}`}>{value}</p>
            <p className="mt-1 text-sm text-slate-400">{label}</p>
          </div>
        ))}
      </div>

      <div className="panel p-5">
        <div className="flex flex-wrap items-center gap-3">
          <div className="min-w-[220px] flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search findings by name or category" className="field py-2.5 pl-10 text-sm" />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-500" />
            <select value={severity} onChange={(event) => setSeverity(event.target.value)} className="field w-auto py-2.5 text-sm">
              <option value="all">All severities</option>
              {['critical', 'high', 'medium', 'low', 'informational'].map((value) => (
                <option key={value} value={value}>{value}</option>
              ))}
            </select>
            <select value={status} onChange={(event) => setStatus(event.target.value)} className="field w-auto py-2.5 text-sm">
              {STATUS_OPTIONS.map((value) => (
                <option key={value} value={value}>{value === 'all' ? 'All statuses' : value.replace('_', ' ')}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-5">
          {loading ? (
            <Loader label="Loading findings..." />
          ) : items.length === 0 ? (
            <EmptyState icon={ShieldAlert} title="No findings match your filters" description="Try a different search term or run a new scan." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[860px] text-left text-sm">
                <thead>
                  <tr className="border-b border-white/[0.07] text-[11px] uppercase tracking-wider text-slate-500">
                    <th className="pb-3 font-medium">Finding</th>
                    <th className="pb-3 font-medium">Category</th>
                    <th className="pb-3 font-medium">Severity</th>
                    <th className="pb-3 font-medium">Score</th>
                    <th className="pb-3 font-medium">Confidence</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3 text-right font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.05]">
                  {items.map((item) => (
                    <tr key={item.id} className="transition hover:bg-white/[0.02]">
                      <td className="max-w-[280px] py-3.5">
                        <p className="truncate font-medium text-slate-200">{item.name}</p>
                        <p className="truncate font-mono text-[10px] text-slate-500">{item.affected_url}</p>
                      </td>
                      <td className="py-3.5 text-xs text-slate-400">{item.category}</td>
                      <td className="py-3.5"><SeverityBadge severity={item.severity} /></td>
                      <td className="py-3.5 font-mono font-semibold text-white">{item.risk_score}</td>
                      <td className="py-3.5 text-xs capitalize text-slate-400">{item.confidence}{item.verified ? ' · verified' : ''}</td>
                      <td className="py-3.5">
                        <select value={item.status} onChange={(event) => updateStatus(item.id, event.target.value)} className="rounded-lg border border-white/10 bg-ink-900 px-2 py-1.5 text-xs text-slate-300">
                          {STATUS_OPTIONS.filter((option) => option !== 'all').map((option) => (
                            <option key={option} value={option}>{option.replace('_', ' ')}</option>
                          ))}
                        </select>
                      </td>
                      <td className="py-3.5 text-right">
                        <button onClick={() => setSelected(item)} className="btn-ghost px-3 py-1.5 text-xs">Details</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <Modal open={Boolean(selected)} onClose={() => setSelected(null)} title={selected?.name || 'Finding details'} description={selected?.affected_url}>
        {selected && (
          <div className="space-y-4">
            <FindingDetails finding={selected} />
            <div className="flex flex-wrap gap-2 border-t border-white/[0.07] pt-4">
              {STATUS_OPTIONS.filter((option) => option !== 'all').map((option) => (
                <button key={option} onClick={() => updateStatus(selected.id, option)} className={`btn-ghost px-3 py-1.5 text-xs capitalize ${selected.status === option ? 'border-electric-400/50 text-electric-300' : ''}`}>
                  {option.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
