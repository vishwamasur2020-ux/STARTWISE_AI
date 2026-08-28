/**
 * STARTWISE AI — Admin Startup Detail Page (Stage 12)
 */

import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, TrendingUp, Users, FileText, Megaphone, Store } from 'lucide-react'
import { useAdminStartup } from '@/hooks/useAdmin'

const RISK_COLORS: Record<string, string> = {
  Low: 'text-green-400 bg-green-500/10 border-green-500/30',
  Medium: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  High: 'text-red-400 bg-red-500/10 border-red-500/30',
}

function Field({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div>
      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-0.5">{label}</p>
      <p className="text-sm font-semibold text-white">{value ?? '—'}</p>
    </div>
  )
}

export default function AdminStartupDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data, isLoading } = useAdminStartup(id ?? '')

  if (isLoading) {
    return (
      <div className="space-y-6 pb-12">
        <div className="h-8 bg-slate-800 rounded w-48 animate-pulse" />
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-6 animate-pulse space-y-4">
          {Array.from({ length: 8 }).map((_, i) => <div key={i} className="h-4 bg-slate-800 rounded w-full" />)}
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-20">
        <p className="text-slate-400">Startup not found.</p>
        <Link to="/admin/startups" className="text-amber-400 text-sm mt-2 inline-block">← Back to Startups</Link>
      </div>
    )
  }

  const s = data as any

  return (
    <div className="space-y-6 pb-12">
      <Link to="/admin/startups" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to Startups
      </Link>

      {/* Header */}
      <div className="bg-slate-900 border border-white/10 rounded-2xl p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-black text-white">{s.business_name}</h1>
            <p className="text-slate-400 text-sm mt-1">{s.business_category} · {s.preferred_location}</p>
            <p className="text-slate-500 text-xs mt-0.5">Owner: {s.owner_name} ({s.owner_email})</p>
          </div>
          <p className="text-xs text-slate-500">Created {new Date(s.created_at).toLocaleDateString()}</p>
        </div>
      </div>

      {/* Counters */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Franchise Recs', value: s.franchise_recs_count, icon: Store, color: 'text-amber-400' },
          { label: 'Marketing Strategies', value: s.marketing_count, icon: Megaphone, color: 'text-cyan-400' },
          { label: 'Reports', value: s.reports_count, icon: FileText, color: 'text-rose-400' },
          { label: 'Employees', value: s.employee_count, icon: Users, color: 'text-indigo-400' },
        ].map(stat => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="bg-slate-900 border border-white/10 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`h-4 w-4 ${stat.color}`} />
                <span className="text-xs text-slate-500 font-semibold">{stat.label}</span>
              </div>
              <p className="text-2xl font-black text-white">{stat.value}</p>
            </div>
          )
        })}
      </div>

      {/* Details Grid */}
      <div className="bg-slate-900 border border-white/10 rounded-2xl p-6">
        <h3 className="text-sm font-bold text-white mb-5">Startup Details</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          <Field label="Business Model" value={s.business_model} />
          <Field label="Target Customers" value={s.target_customers} />
          <Field label="Investment Amount" value={`₹${s.investment_amount?.toLocaleString('en-IN')}`} />
          <Field label="Expected Monthly Revenue" value={`₹${s.expected_monthly_revenue?.toLocaleString('en-IN')}`} />
          <Field label="Market Demand" value={`${s.market_demand}/10`} />
          <Field label="Competition Level" value={s.competition_level} />
          <Field label="Experience Years" value={`${s.experience_years} years`} />
          <Field label="Employee Count" value={s.employee_count} />
        </div>
        {s.description && (
          <div className="mt-5 pt-5 border-t border-white/10">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Description</p>
            <p className="text-sm text-slate-300">{s.description}</p>
          </div>
        )}
      </div>

      {/* Prediction Results */}
      {s.prediction ? (
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-5">
            <TrendingUp className="h-4 w-4 text-green-400" />
            <h3 className="text-sm font-bold text-white">AI Prediction Results</h3>
            <span className="text-[10px] text-slate-500 ml-auto">Read-only — generated by ML model</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            <div className="bg-slate-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-slate-500 mb-1">Business Score</p>
              <p className="text-2xl font-black text-white">{s.prediction.business_score?.toFixed(1)}</p>
            </div>
            <div className="bg-slate-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-slate-500 mb-1">Success Prob.</p>
              <p className="text-2xl font-black text-green-400">{s.prediction.success_probability?.toFixed(1)}%</p>
            </div>
            <div className="bg-slate-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-slate-500 mb-1">Risk Level</p>
              <span className={`text-xs font-bold px-2 py-1 rounded-full border ${RISK_COLORS[s.prediction.risk_level] || 'text-slate-400 bg-slate-700 border-white/10'}`}>
                {s.prediction.risk_level}
              </span>
            </div>
            <div className="bg-slate-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-slate-500 mb-1">Estimated ROI</p>
              <p className="text-2xl font-black text-cyan-400">{s.prediction.estimated_roi?.toFixed(1)}%</p>
            </div>
            <div className="bg-slate-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-slate-500 mb-1">Confidence</p>
              <p className="text-2xl font-black text-violet-400">{s.prediction.confidence_score?.toFixed(1)}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-6 text-center">
          <p className="text-slate-500 text-sm">No AI analysis has been performed for this startup yet.</p>
        </div>
      )}
    </div>
  )
}
