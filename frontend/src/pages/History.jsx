import { useCallback, useEffect, useState } from 'react'
import { ArrowDownRight, ArrowUpRight, Download, History as HistoryIcon, RotateCcw, Search, Trash2 } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import SeverityBadge from '../components/SeverityBadge'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import FindingDetails from '../components/FindingDetails'
import EmptyState from '../components/EmptyState'
import Loader from '../components/Loader'
import { historyService } from '../services/historyService'
import { scanService } from '../services/scanService'
import { reportService } from '../services/reportService'
import { useToast } from '../hooks/useToast'

export default function ScanHistoryPage() {
  const toast = useToast()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [detail, setDetail] = useState(null)
  const [finding, setFinding] = useState(null)
  const [confirm, setConfirm] = useState(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    try {
      const data = await historyService.list(200)
      setItems(data.history)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const remove = async () => {
    if (!confirm) return
    setBusy(true)
    try {
      if (confirm === 'all') {
        const result = await historyService.clear()
        toast.success(result.message)
      } else {
        const result = await historyService.remove(confirm)
        toast.success(result.message)
      }
      setConfirm(null)
      setDetail(null)
      await load()
    } catch (error) {
      toast.error(error.message)
    } finally {
      setBusy(false)
    }
  }

  const retry = async (scanId) => {
    try {
      await scanService.retry(scanId)
      toast.info('Scan restarted')
      await load()
    } catch (error) {
      toast.error(error.message)
    }
  }

  const download = async (scanId, format) => {
    try {
      if (format === 'pdf') await reportService.downloadPdf(scanId)
      else await reportService.downloadCsv(scanId)
      toast.success(`${format.toUpperCase()} report downloaded`)
    } catch (error) {
      toast.error(error.message)
    }
  }

  const filtered = items.filter((item) => {
    const matchSearch = item.target_url.toLowerCase().includes(search.toLowerCase()) || item.id.toLowerCase().includes(search.toLowerCase())
    const matchStatus = status === 'all' || item.status === status
    return matchSearch && matchStatus
  })

  return (
    <div className="space-y-6">
      <div className="panel flex flex-wrap items-center justify-between gap-4 p-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-electric-500/25 bg-electric-500/10 text-electric-300">
            <HistoryIcon className="h-5 w-5" />
          </div>
          <div>
            <h2 className="section-title">Scan history</h2>
            <p className="muted text-xs">Review, compare and manage previous security assessments.</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search history" className="field py-2.5 pl-10 text-sm" />
          </div>
          <select value={status} onChange={(event) => setStatus(event.target.value)} className="field w-auto py-2.5 text-sm">
            {['all', 'completed', 'running', 'queued', 'failed'].map((value) => (
              <option key={value} value={value}>{value === 'all' ? 'All statuses' : value}</option>
            ))}
          </select>
          {items.length > 0 && <button onClick={() => setConfirm('all')} className="btn-danger text-xs"><Trash2 className="h-3.5 w-3.5" /> Clear all</button>}
        </div>
      </div>

      {loading ? (
        <Loader label="Loading scan history..." />
      ) : filtered.length === 0 ? (
        <EmptyState icon={HistoryIcon} title="No scan history" description="Your previous assessments will appear here." />
      ) : (
        <div className="panel overflow-x-auto p-5">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead>
              <tr className="border-b border-white/[0.07] text-[11px] uppercase tracking-wider text-slate-500">
                <th className="pb-3 font-medium">Target</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium">Findings</th>
                <th className="pb-3 font-medium">Score</th>
                <th className="pb-3 font-medium">Change</th>
                <th className="pb-3 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {filtered.map((scan) => (
                <tr key={scan.id} className="transition hover:bg-white/[0.02]">
                  <td className="py-3.5">
                    <p className="font-medium text-slate-200">{scan.target_host}</p>
                    <p className="max-w-[230px] truncate font-mono text-[10px] text-slate-500">{scan.id}</p>
                  </td>
                  <td className="py-3.5"><StatusBadge status={scan.status} /></td>
                  <td className="py-3.5 text-xs text-slate-400">{new Date(scan.created_at).toLocaleString()}</td>
                  <td className="py-3.5 font-mono text-slate-300">{scan.total_findings}</td>
                  <td className="py-3.5 font-mono font-bold text-white">{scan.security_score}</td>
                  <td className="py-3.5">
                    {scan.score_change === null || scan.score_change === undefined ? (
                      <span className="text-xs text-slate-600">First scan</span>
                    ) : (
                      <span className={`inline-flex items-center gap-1 text-xs font-semibold ${scan.score_change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {scan.score_change >= 0 ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                        {Math.abs(scan.score_change)} pts
                      </span>
                    )}
                  </td>
                  <td className="py-3.5">
                    <div className="flex justify-end gap-2">
                      <button onClick={() => scanService.get(scan.id).then((data) => setDetail(data.scan)).catch((error) => toast.error(error.message))} className="btn-ghost px-2.5 py-1.5 text-xs">View</button>
                      {scan.status === 'completed' && (
                        <>
                          <button onClick={() => download(scan.id, 'pdf')} className="btn-ghost px-2.5 py-1.5 text-xs" title="PDF"><Download className="h-3.5 w-3.5" /></button>
                          <button onClick={() => download(scan.id, 'csv')} className="btn-ghost px-2.5 py-1.5 text-xs" title="CSV">CSV</button>
                        </>
                      )}
                      <button onClick={() => retry(scan.id)} className="btn-ghost px-2.5 py-1.5 text-xs" title="Rescan"><RotateCcw className="h-3.5 w-3.5" /></button>
                      <button onClick={() => setConfirm(scan.id)} className="btn-danger px-2.5 py-1.5 text-xs" title="Delete"><Trash2 className="h-3.5 w-3.5" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={Boolean(detail)} onClose={() => setDetail(null)} title="Scan details" description={detail?.target_url} width="max-w-3xl">
        {detail && (
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                ['Status', detail.status],
                ['Score', detail.security_score],
                ['Findings', detail.total_findings],
                ['Pages', detail.pages_scanned],
              ].map(([label, value]) => (
                <div key={label} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
                  <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
                  <p className="mt-1 font-mono text-base font-bold text-white">{value}</p>
                </div>
              ))}
            </div>
            <div>
              <p className="label">Findings</p>
              {detail.vulnerabilities.length === 0 ? (
                <p className="muted">No findings recorded.</p>
              ) : (
                <div className="space-y-2">
                  {detail.vulnerabilities.map((item) => (
                    <button key={item.id} onClick={() => setFinding(item)} className="flex w-full items-center gap-3 rounded-xl border border-white/[0.07] bg-white/[0.02] p-3 text-left transition hover:border-electric-400/30">
                      <span className="min-w-0 flex-1 truncate text-sm text-slate-200">{item.name}</span>
                      <SeverityBadge severity={item.severity} />
                      <span className="font-mono text-xs text-white">{item.risk_score}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>

      <Modal open={Boolean(finding)} onClose={() => setFinding(null)} title={finding?.name || 'Finding details'} width="max-w-3xl">
        <FindingDetails finding={finding} />
      </Modal>

      <ConfirmDialog
        open={Boolean(confirm)}
        onClose={() => setConfirm(null)}
        onConfirm={remove}
        busy={busy}
        danger
        title={confirm === 'all' ? 'Clear all scan history?' : 'Delete this scan?'}
        message={confirm === 'all' ? 'This permanently removes all scans and their findings. This action cannot be undone.' : 'This permanently removes the scan and all of its findings.'}
        confirmLabel="Delete"
      />
    </div>
  )
}
