import type { LucideIcon } from 'lucide-react'

export function MetricCard({ icon: Icon, label, value, detail, accent = 'blue' }: { icon: LucideIcon; label: string; value: string; detail: string; accent?: 'blue' | 'green' }) {
  const colors = accent === 'green' ? 'bg-emerald-400/10 text-emerald-300' : 'bg-sky-400/10 text-sky-300'
  return <article className="card"><div className="flex items-start justify-between"><div><p className="label">{label}</p><p className="mt-3 text-2xl font-semibold tracking-tight text-white">{value}</p></div><span className={`rounded-xl p-2.5 ${colors}`}><Icon size={20}/></span></div><p className="mt-4 text-xs text-slate-400">{detail}</p></article>
}
