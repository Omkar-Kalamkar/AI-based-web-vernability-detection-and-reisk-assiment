import { useCallback, useEffect, useState } from 'react'
import { BrainCircuit, CheckCircle2, CircleHelp, Cpu, Sparkles } from 'lucide-react'
import ScoreRing from '../components/ScoreRing'
import SeverityBadge from '../components/SeverityBadge'
import EmptyState from '../components/EmptyState'
import Loader from '../components/Loader'
import { aiService } from '../services/aiService'
import { scanService } from '../services/scanService'
import { useToast } from '../hooks/useToast'

export default function RiskAssessment() {
  const toast = useToast()
  const [scans, setScans] = useState([])
  const [scanId, setScanId] = useState('')
  const [assessment, setAssessment] = useState(null)
  const [validation, setValidation] = useState(null)
  const [model, setModel] = useState(null)
  const [loading, setLoading] = useState(false)
  const [explainForm, setExplainForm] = useState({ name: '', category: '' })
  const [explanation, setExplanation] = useState(null)

  useEffect(() => {
    Promise.all([scanService.list(100), aiService.modelInfo()])
      .then(([scanData, modelData]) => {
        const completed = scanData.scans.filter((item) => item.status === 'completed')
        setScans(completed)
        if (completed.length) setScanId((current) => current || completed[0].id)
        setModel(modelData)
      })
      .catch((error) => toast.error(error.message))
  }, [])

  const load = useCallback(async () => {
    if (!scanId) return
    setLoading(true)
    try {
      const [assessmentData, validationData] = await Promise.all([
        aiService.assessment(scanId),
        aiService.validation(scanId),
      ])
      setAssessment(assessmentData.assessment)
      setValidation(validationData)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }, [scanId])

  useEffect(() => {
    load()
  }, [load])

  const explain = async (event) => {
    event.preventDefault()
    try {
      const data = await aiService.explain(explainForm)
      setExplanation(data.explanation)
    } catch (error) {
      toast.error(error.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="panel flex flex-wrap items-center justify-between gap-4 p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-violet-500/25 bg-violet-500/10 text-violet-300">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <h2 className="section-title">AI risk assessment engine</h2>
            <p className="muted text-xs">Transparent weighted scoring with local knowledge-based explanations.</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="chip"><Cpu className="h-3 w-3" /> {model?.model?.available ? 'Synthetic ML demo enabled' : 'Rule-based model active'}</span>
          <select value={scanId} onChange={(event) => setScanId(event.target.value)} className="field w-auto max-w-xs py-2.5 text-sm">
            {scans.length === 0 && <option value="">No completed scans</option>}
            {scans.map((scan) => (
              <option key={scan.id} value={scan.id}>{scan.target_host} · {new Date(scan.created_at).toLocaleDateString()}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <Loader label="Analyzing findings..." />
      ) : !assessment ? (
        <EmptyState icon={BrainCircuit} title="No assessment available" description="Complete a scan first to generate an AI risk assessment." />
      ) : (
        <>
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="panel p-6">
              <ScoreRing score={assessment.security_score} label="Overall security score" subtitle={assessment.target_url} />
            </div>
            <div className="panel p-6 lg:col-span-2">
              <h3 className="section-title">Risk summary</h3>
              <p className="muted mt-3">{assessment.risk_summary}</p>
              <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  ['Confirmed', assessment.confirmed_findings, 'text-emerald-300'],
                  ['Potential', assessment.potential_indicators, 'text-amber-300'],
                  ['Findings', Object.values(assessment.severity_distribution).reduce((a, b) => a + b, 0), 'text-white'],
                  ['Model', assessment.model?.available ? 'Synthetic ML' : 'Rules', 'text-electric-300'],
                ].map(([label, value, color]) => (
                  <div key={label} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
                    <p className={`font-mono text-lg font-bold ${color}`}>{value}</p>
                    <p className="text-[11px] text-slate-500">{label}</p>
                  </div>
                ))}
              </div>
              <div className="mt-5 space-y-2">
                {assessment.recommended_next_steps.map((step) => (
                  <p key={step} className="flex items-center gap-2 text-xs text-slate-400"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" /> {step}</p>
                ))}
              </div>
            </div>
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <div className="panel p-6">
              <h3 className="section-title">Top risks and reasoning</h3>
              {assessment.top_risks.length === 0 ? (
                <p className="muted mt-4">No findings to assess for this scan.</p>
              ) : (
                <div className="mt-5 space-y-4">
                  {assessment.top_risks.map((risk) => (
                    <div key={risk.name} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="text-sm font-semibold text-slate-200">{risk.name}</p>
                        <div className="flex items-center gap-2"><SeverityBadge severity={risk.severity} /><span className="font-mono text-xs text-white">{risk.risk_score}</span></div>
                      </div>
                      <ul className="mt-3 space-y-1.5">
                        {risk.reasoning.map((line, index) => (
                          <li key={index} className="flex gap-2 text-[11px] leading-relaxed text-slate-400"><span className="text-electric-400">•</span>{line}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="panel p-6">
                <h3 className="section-title">False-positive reduction</h3>
                {validation && (
                  <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    {[
                      ['Total findings', validation.total_findings],
                      ['Verified observations', validation.verified_findings],
                      ['Potential indicators', validation.potential_indicators],
                      ['Evidence coverage', `${validation.evidence_coverage}/${validation.total_findings}`],
                    ].map(([label, value]) => (
                      <div key={label} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
                        <p className="font-mono text-lg font-bold text-white">{value}</p>
                        <p className="text-[11px] text-slate-500">{label}</p>
                      </div>
                    ))}
                  </div>
                )}
                <p className="muted mt-4 text-xs">{validation?.method}</p>
              </div>

              <div className="panel p-6">
                <h3 className="section-title">Model transparency</h3>
                <div className="mt-4 space-y-2 text-xs text-slate-400">
                  <p><span className="font-semibold text-slate-200">Status:</span> {model?.model?.note}</p>
                  <p><span className="font-semibold text-slate-200">Features:</span> {model?.model?.features?.join(', ')}</p>
                  <p><span className="font-semibold text-slate-200">Thresholds:</span> critical ≥85, high ≥70, medium ≥45, low ≥20.</p>
                  <p><span className="font-semibold text-slate-200">Explanations:</span> {model?.explanation_source}</p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      <div className="panel p-6">
        <div className="flex items-center gap-3">
          <Sparkles className="h-5 w-5 text-violet-300" />
          <div>
            <h3 className="section-title">Explain a custom finding</h3>
            <p className="muted text-xs">Generate beginner-friendly guidance from a vulnerability name or category.</p>
          </div>
        </div>
        <form onSubmit={explain} className="mt-5 grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
          <input value={explainForm.name} onChange={(event) => setExplainForm({ ...explainForm, name: event.target.value })} className="field" placeholder="Finding name (optional)" />
          <input value={explainForm.category} onChange={(event) => setExplainForm({ ...explainForm, category: event.target.value })} className="field" placeholder="Category, e.g. Cookie Security" />
          <button type="submit" className="btn-primary"><CircleHelp className="h-4 w-4" /> Explain</button>
        </form>
        {explanation && (
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {Object.entries(explanation).map(([key, value]) => (
              <div key={key} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-4">
                <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-electric-300">{key.replaceAll('_', ' ')}</p>
                <p className="text-xs leading-relaxed text-slate-300">{value}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
