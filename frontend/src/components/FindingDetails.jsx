import { AlertCircle, BookOpen, CheckCircle2, Code2, ExternalLink, Lightbulb, Link2, ShieldCheck } from 'lucide-react'
import SeverityBadge from './SeverityBadge'

function Section({ icon: Icon, title, children, tone = 'blue' }) {
  const tones = {
    blue: 'text-electric-300 border-electric-500/20 bg-electric-500/[0.06]',
    green: 'text-emerald-300 border-emerald-500/20 bg-emerald-500/[0.06]',
    amber: 'text-amber-300 border-amber-500/20 bg-amber-500/[0.06]',
    red: 'text-red-300 border-red-500/20 bg-red-500/[0.06]',
  }
  return (
    <div className={`rounded-xl border p-4 ${tones[tone]}`}>
      <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.12em]">
        <Icon className="h-4 w-4" />
        {title}
      </div>
      <div className="text-sm leading-relaxed text-slate-300">{children}</div>
    </div>
  )
}

export default function FindingDetails({ finding }) {
  if (!finding) return null
  const fields = [
    ['Category', finding.category],
    ['Confidence', finding.confidence],
    ['Validation', finding.verified ? 'Confirmed observation' : 'Potential indicator — requires manual review'],
    ['Affected URL', finding.affected_url],
    ['Affected endpoints', finding.affected_endpoints],
    ['Exploitability', finding.exploitability],
    ['Risk model', finding.model_source],
  ]

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <SeverityBadge severity={finding.severity} size="lg" />
        <span className="chip">Risk score <span className="font-mono font-bold text-white">{finding.risk_score}</span>/100</span>
        {finding.verified ? (
          <span className="chip text-emerald-300"><CheckCircle2 className="h-3 w-3" /> Evidence verified</span>
        ) : (
          <span className="chip text-amber-300"><AlertCircle className="h-3 w-3" /> Indicative only</span>
        )}
      </div>

      <p className="text-sm leading-relaxed text-slate-300">{finding.description}</p>

      <div className="grid gap-2 sm:grid-cols-2">
        {fields.map(([label, value]) => (
          <div key={label} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">{label}</p>
            <p className="mt-1 break-all text-sm text-slate-200">{value || '-'}</p>
          </div>
        ))}
      </div>

      <Section icon={Lightbulb} title="In simple terms">{finding.simple_explanation}</Section>
      <Section icon={AlertCircle} title="Why it is dangerous" tone="red">{finding.why_dangerous}</Section>
      <Section icon={ShieldCheck} title="Potential impact" tone="amber">{finding.impact}</Section>
      <Section icon={Link2} title="Evidence">{finding.evidence || 'No evidence recorded.'}</Section>
      <Section icon={CheckCircle2} title="Recommended fix" tone="green">{finding.recommendation}</Section>
      <Section icon={Code2} title="Secure coding practice">{finding.secure_coding}</Section>
      <Section icon={BookOpen} title="Prevention">{finding.prevention}</Section>

      {Array.isArray(finding.reasoning) && finding.reasoning.length > 0 && (
        <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">Transparent risk reasoning</p>
          <ol className="list-decimal space-y-1 pl-5 text-xs leading-relaxed text-slate-400">
            {finding.reasoning.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ol>
        </div>
      )}

      {Array.isArray(finding.references) && finding.references.length > 0 && (
        <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">References</p>
          <div className="flex flex-wrap gap-2">
            {finding.references.map((reference) => (
              <a key={reference} href={reference} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 rounded-lg border border-electric-500/20 bg-electric-500/10 px-2.5 py-1.5 text-xs text-electric-300 hover:bg-electric-500/20">
                {reference} <ExternalLink className="h-3 w-3" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
