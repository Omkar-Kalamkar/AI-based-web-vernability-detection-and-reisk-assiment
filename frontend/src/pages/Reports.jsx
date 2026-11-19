import { useEffect, useState } from 'react'
import { Download, FileBarChart2, FileSpreadsheet, FileText, Search } from 'lucide-react'
import EmptyState from '../components/EmptyState'
import Loader from '../components/Loader'
import StatusBadge from '../components/StatusBadge'
import ScoreRing from '../components/ScoreRing'
import { scanService } from '../services/scanService'
import { reportService } from '../services/reportService'
import { useToast } from '../hooks/useToast'

export default function Reports() {
  const toast = useToast()
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    scanService.list(100)
      .then((data) => setScans(data.scans.filter((item) => item.status === 'completed')))
      .catch((error) => toast.error(error.message))
      .finally(() => setLoading(false))
  }, [])

  const download = async (scanId, format) => {
    try {
      if (format === 'pdf') await reportService.downloadPdf(scanId)
      else await reportService.downloadCsv(scanId)
      toast.success(`${format.toUpperCase()} report downloaded`)
    } catch (error) {
      toast.error(error.message)
    }
  }

  const filtered = scans.filter((scan) => scan.target_url.toLowerCase().includes(search.toLowerCase()) || scan.id.includes(search.toLowerCase()))

  return (
    <div className="space-y-6">
      <div className="panel overflow-hidden p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-electric-500/25 bg-electric-500/10 text-electric-300">
              <FileBarChart2 className="h-5 w-5" />
            </div>
            <div>
              <h2 className="section-title">Security reports</h2>
              <p className="muted text-xs">Download PDF and CSV reports for completed assessments.</p>
            </div>
          </div>
          <div className="relative w-full max-w-xs">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Filter by target or ID" className="field py-2.5 pl-10 text-sm" />
          </div>
        </div>
      </div>

      {loading ? (
        <Loader label="Loading reports..." />
      ) : filtered.length === 0 ? (
        <EmptyState icon={FileText} title="No reports available" description="Reports are generated after a scan completes. Run a scan to create your first report." />
      ) : (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((scan) => (
            <div key={scan.id} className="panel panel-hover p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <StatusBadge status={scan.status} />
                  <h3 className="mt-3 truncate font-display text-base font-semibold text-white">{scan.target_host}</h3>
                  <p className="truncate font-mono text-[11px] text-slate-500">{scan.target_url}</p>
                </div>
                <ScoreRing score={scan.security_score} size={66} label="" />
              </div>
              <div className="mt-5 grid grid-cols-3 gap-2 text-center">
                {[
                  ['Findings', scan.total_findings],
                  ['Critical', scan.severity_counts.critical],
                  ['High', scan.severity_counts.high],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-lg border border-white/[0.07] bg-white/[0.02] p-2">
                    <p className="font-mono text-sm font-bold text-white">{value}</p>
                    <p className="text-[10px] text-slate-500">{label}</p>
                  </div>
                ))}
              </div>
              <p className="mt-4 text-[11px] text-slate-500">Created {new Date(scan.created_at).toLocaleString()}</p>
              <div className="mt-4 flex gap-2">
                <button onClick={() => download(scan.id, 'pdf')} className="btn-primary flex-1 text-xs"><Download className="h-3.5 w-3.5" /> PDF</button>
                <button onClick={() => download(scan.id, 'csv')} className="btn-ghost flex-1 text-xs"><Download className="h-3.5 w-3.5" /> CSV</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="panel grid gap-4 p-6 sm:grid-cols-3">
        {[
          [FileText, 'Complete scan details', 'Target, date, score and severity distribution.'],
          [FileSpreadsheet, 'Structured CSV', 'Every finding with evidence and remediation in columns.'],
          [Download, 'Beginner-friendly guidance', 'Simple explanations and secure coding notes included.'],
        ].map(([Icon, title, description]) => (
          <div key={title} className="flex gap-3">
            <Icon className="h-5 w-5 shrink-0 text-electric-300" />
            <div>
              <p className="text-sm font-semibold text-slate-200">{title}</p>
              <p className="mt-1 text-xs text-slate-500">{description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
