import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AlertTriangle, CheckCircle2, Download, FileText, Info, Loader2, Play, RotateCcw, ScanLine, ShieldCheck, XCircle } from 'lucide-react'
import ProgressBar from '../components/ProgressBar'
import SeverityBadge from '../components/SeverityBadge'
import ScoreRing from '../components/ScoreRing'
import Modal from '../components/Modal'
import FindingDetails from '../components/FindingDetails'
import EmptyState from '../components/EmptyState'
import StatusBadge from '../components/StatusBadge'
import { scanService } from '../services/scanService'
import { settingsService } from '../services/settingsService'
import { reportService } from '../services/reportService'
import { vulnerabilityService } from '../services/vulnerabilityService'
import { useToast } from '../hooks/useToast'
import { usePolling } from '../hooks/usePolling'

export default function NewScan() {
  const toast = useToast()
  const [searchParams] = useSearchParams()
  const [target, setTarget] = useState('http://127.0.0.1:8000')
  const [authorized, setAuthorized] = useState(false)
  const [busy, setBusy] = useState(false)
  const [scanId, setScanId] = useState(null)
  const [scan, setScan] = useState(null)
  const [selected, setSelected] = useState(null)
  const [platform, setPlatform] = useState(null)
  const scanParam = searchParams.get('scan')

  useEffect(() => {
    settingsService.platform().then((data) => setPlatform(data.platform)).catch(() => {})
  }, [])

  const loadScan = useCallback(async () => {
    if (!scanId) return
    const data = await scanService.get(scanId)
    setScan(data.scan)
  }, [scanId])

  const polling = Boolean(scanId) && ['queued', 'running'].includes(scan?.status)
  usePolling(loadScan, 1800, polling)

  useEffect(() => {
    if (scanParam && scanParam !== scanId) {
      setScanId(scanParam)
      scanService.get(scanParam).then((data) => setScan(data.scan)).catch((error) => toast.error(error.message))
    }
  }, [scanParam])

  const start = async (event) => {
    event.preventDefault()
    if (!authorized) {
      toast.error('Please confirm you are authorized to test this target')
      return
    }
    setBusy(true)
    try {
      const result = await scanService.create(target)
      setScanId(result.scan.id)
      setScan(result.scan)
      toast.success('Scan started', 'Authorization confirmed')
    } catch (error) {
      toast.error(error.message, 'Scan could not start')
    } finally {
      setBusy(false)
    }
  }

  const download = async (format) => {
    if (!scanId) return
    try {
      if (format === 'pdf') await reportService.downloadPdf(scanId)
      else await reportService.downloadCsv(scanId)
      toast.success(`${format.toUpperCase()} report downloaded`)
    } catch (error) {
      toast.error(error.message)
    }
  }

  const retry = async () => {
    if (!scanId) return
    try {
      const result = await scanService.retry(scanId)
      setScan(result.scan)
      toast.info('Scan restarted with the same authorized target')
    } catch (error) {
      toast.error(error.message)
    }
  }

  const updateStatus = async (status) => {
    if (!selected) return
    try {
      const result = await vulnerabilityService.updateStatus(selected.id, status)
      setSelected(result.vulnerability)
      setScan((current) => ({
        ...current,
        vulnerabilities: current.vulnerabilities.map((item) => (item.id === result.vulnerability.id ? result.vulnerability : item)),
      }))
      toast.success(`Finding marked as ${status.replace('_', ' ')}`)
    } catch (error) {
      toast.error(error.message)
    }
  }

  const findings = scan?.vulnerabilities || []
  const running = scan && ['queued', 'running'].includes(scan.status)

  return (
    <div className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-[1fr_1.15fr]">
        <div className="panel p-6">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-electric-500/25 bg-electric-500/10 text-electric-300">
              <ScanLine className="h-5 w-5" />
            </div>
            <div>
              <h2 className="section-title">Configure a security scan</h2>
              <p className="muted text-xs">Passive, non-destructive checks with strict scope validation.</p>
            </div>
          </div>

          <form onSubmit={start} className="space-y-5">
            <div>
              <label className="label">Target URL</label>
              <input value={target} onChange={(event) => setTarget(event.target.value)} className="field font-mono text-sm" placeholder="http://127.0.0.1:8000" />
              <p className="mt-2 text-xs text-slate-500">Example: the local vulnerable lab at http://127.0.0.1:8000</p>
            </div>

            <label className={`flex cursor-pointer items-start gap-3 rounded-xl border p-4 transition ${authorized ? 'border-emerald-500/30 bg-emerald-500/[0.07]' : 'border-white/10 bg-white/[0.02]'}`}>
              <input type="checkbox" checked={authorized} onChange={(event) => setAuthorized(event.target.checked)} className="mt-0.5 h-4 w-4 accent-electric-500" />
              <span className="text-sm leading-relaxed text-slate-300">
                I confirm that I own this application or have explicit written authorization to test it, and I agree to non-destructive scanning only.
              </span>
            </label>

            <button type="submit" className="btn-primary w-full" disabled={busy || !authorized}>
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              {busy ? 'Starting scan...' : 'Start secure scan'}
            </button>
          </form>

          <div className="mt-6 space-y-3 border-t border-white/[0.07] pt-5">
            <div className="flex items-start gap-2 text-xs text-slate-400">
              <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
              GET-only requests, short timeouts and a maximum page limit are enforced by the server.
            </div>
            <div className="flex items-start gap-2 text-xs text-slate-400">
              <Info className="mt-0.5 h-4 w-4 shrink-0 text-electric-400" />
              {platform ? (
                <>Lab mode is <span className="font-semibold text-emerald-300">{platform.local_lab_mode ? 'enabled' : 'disabled'}</span>. Allowed hosts: {platform.allowed_lab_hosts.join(', ')}. Ports: {platform.allowed_lab_ports.join(', ')}.</>
              ) : (
                'Loading platform scan limits...'
              )}
            </div>
            <div className="flex items-start gap-2 text-xs text-slate-400">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
              Potential XSS/SQL indicators are validated with benign observations and never reported as confirmed exploits.
            </div>
          </div>
        </div>

        <div className="panel p-6">
          {!scan ? (
            <EmptyState
              icon={ScanLine}
              title="No active scan"
              description="Configure a target on the left and start a scan. Progress and findings will appear here in real time."
            />
          ) : (
            <div className="space-y-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2"><StatusBadge status={scan.status} /><span className="chip">{scan.scan_mode}</span></div>
                  <h3 className="mt-3 font-display text-lg font-semibold text-white">Scan results</h3>
                  <p className="break-all font-mono text-xs text-slate-400">{scan.target_url}</p>
                  <p className="mt-1 text-[11px] text-slate-500">ID: {scan.id} · {scan.pages_scanned} pages inspected</p>
                </div>
                <ScoreRing score={scan.security_score} size={92} label="" />
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-300">{scan.stage}</span>
                  <span className="font-mono text-electric-300">{scan.progress}%</span>
                </div>
                <ProgressBar value={scan.progress} tone={scan.status === 'failed' ? 'red' : 'blue'} />
              </div>

              {scan.error && (
                <div className="flex items-start gap-2 rounded-xl border border-red-500/25 bg-red-500/10 p-3 text-sm text-red-200">
                  <XCircle className="mt-0.5 h-4 w-4 shrink-0" /> {scan.error}
                </div>
              )}

              {running && (
                <div className="flex items-center gap-2 rounded-xl border border-electric-500/20 bg-electric-500/[0.06] p-3 text-sm text-electric-200">
                  <Loader2 className="h-4 w-4 animate-spin" /> Scan in progress — results update automatically.
                </div>
              )}

              {scan.status === 'completed' && (
                <>
                  <div className="grid grid-cols-5 gap-2">
                    {[
                      ['critical', scan.severity_counts.critical],
                      ['high', scan.severity_counts.high],
                      ['medium', scan.severity_counts.medium],
                      ['low', scan.severity_counts.low],
                      ['informational', scan.severity_counts.informational],
                    ].map(([label, value]) => (
                      <div key={label} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-2.5 text-center">
                        <p className="font-mono text-lg font-bold text-white">{value}</p>
                        <p className="truncate text-[10px] capitalize text-slate-500">{label}</p>
                      </div>
                    ))}
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button onClick={() => download('pdf')} className="btn-ghost text-xs"><Download className="h-3.5 w-3.5" /> PDF report</button>
                    <button onClick={() => download('csv')} className="btn-ghost text-xs"><FileText className="h-3.5 w-3.5" /> CSV report</button>
                    <button onClick={retry} className="btn-ghost text-xs"><RotateCcw className="h-3.5 w-3.5" /> Rescan</button>
                  </div>

                  <div>
                    <p className="label">Detected findings ({findings.length})</p>
                    {findings.length === 0 ? (
                      <EmptyState icon={CheckCircle2} title="No issues detected" description="No supported findings were observed for this target." />
                    ) : (
                      <div className="max-h-[420px] space-y-2 overflow-y-auto pr-1">
                        {findings.map((finding) => (
                          <button key={finding.id} onClick={() => setSelected(finding)} className="flex w-full items-center gap-3 rounded-xl border border-white/[0.07] bg-white/[0.02] p-3 text-left transition hover:border-electric-400/30 hover:bg-white/[0.05]">
                            <span className="font-mono text-xs text-slate-500">#{finding.risk_score}</span>
                            <span className="min-w-0 flex-1">
                              <span className="block truncate text-sm font-medium text-slate-200">{finding.name}</span>
                              <span className="block truncate text-[11px] text-slate-500">{finding.category} · {finding.verified ? 'verified' : 'potential indicator'}</span>
                            </span>
                            <SeverityBadge severity={finding.severity} />
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              )}

              {scan.status === 'failed' && (
                <button onClick={retry} className="btn-primary"><RotateCcw className="h-4 w-4" /> Retry scan</button>
              )}
            </div>
          )}
        </div>
      </div>

      <Modal
        open={Boolean(selected)}
        onClose={() => setSelected(null)}
        title={selected?.name || 'Finding details'}
        description={selected ? `${selected.category} · ${selected.affected_url}` : ''}
      >
        {selected && (
          <div className="space-y-4">
            <FindingDetails finding={selected} />
            <div className="flex flex-wrap gap-2 border-t border-white/[0.07] pt-4">
              <span className="mr-auto self-center text-xs text-slate-500">Update workflow status:</span>
              {['open', 'in_progress', 'resolved', 'false_positive'].map((status) => (
                <button key={status} onClick={() => updateStatus(status)} className={`btn-ghost px-3 py-1.5 text-xs capitalize ${selected.status === status ? 'border-electric-400/50 text-electric-300' : ''}`}>
                  {status.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
