import { Inbox } from 'lucide-react'

export default function EmptyState({ icon: Icon = Inbox, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-14 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-electric-500/20 bg-electric-500/10">
        <Icon className="h-6 w-6 text-electric-300" />
      </div>
      <h3 className="font-display text-base font-semibold text-white">{title}</h3>
      {description && <p className="muted mt-2 max-w-md">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
