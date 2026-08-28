/**
 * STARTWISE AI — Admin Predictions Monitoring Page (Stage 12)
 */

import { useState } from 'react'
import { Search, ChevronLeft, ChevronRight, X } from 'lucide-react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, Legend
} from 'recharts'
import { useAdminPredictions } from '@/hooks/useAdmin'

const RISK_COLORS = { Low: '#10b981', Medium: '#f59e0b', High: '#ef4444' }
const BAR_COLORS = ['#06b6d4', '#6366f1', '#f59e0b', '#10b981', '#f43f5e']

export default function AdminPredictionsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const params = { page, per_page: 20, search: search || undefined }
  const { data, isLoading } = useAdminPredictions(params)
  const items = (data as any)?.items ?? []
  const total = (data as any)?.total ?? 0
  const pages = (data as any)?.pages ?? 1

  // Compute chart data from current page
  const riskCounts: Record<string, number> = {}
  let sumScore = 0, sumProb = 0, sumRoi = 0
  items.forEach((p: any) => {
    riskCounts[p.risk_level] = (riskCounts[p.risk_level] || 0) + 1
    sumScore += p.business_score
    sumProb += p.success_probability
    sumRoi += p.estimated_roi
  })
  const n = items.length || 1

  const riskPieData = Object.entries(riskCounts).map(([k, v]) => ({ name: k, value: v }))
  const avgBarData = [
    { name: 'Bus. Score', value: +(sumScore / n).toFixed(1) },
    { name: 'Success Prob.', value: +(sumProb / n).toFixed(1) },
    { name: 'ROI %', value: +(sumRoi / n).toFixed(1) },
  ]

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-black text-white">Prediction Monitoring</h1>
        <p className="text-sm text-slate-400 mt-1">{total} total AI predictions</p>
      </div>

      {/* Charts */}
      {!isLoading && items.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-white/10 rounded-2xl p-5">
            <h3 className="text-sm font-bold text-white mb-4">Average Metrics (Current Page)</h3>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={avgBarData} barSize={40}>
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {avgBarData.map((_, i) => <Cell key={i} fill={BAR_COLORS[i]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-slate-900 border border-white/10 rounded-2xl p-5">
            <h3 className="text-sm font-bold text-white mb-4">Risk Distribution</h3>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={riskPieData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                  {riskPieData.map((entry, i) => (
                    <Cell key={i} fill={RISK_COLORS[entry.name as keyof typeof RISK_COLORS] || '#64748b'} />
                  ))}
                </Pie>
                <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{v}</span>} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1) }}
            placeholder="Search startup name…"
            className="w-full pl-9 pr-4 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
          />
        </div>
        {search && (
          <button onClick={() => { setSearch(''); setPage(1) }} className="flex items-center gap-1.5 px-3 py-2.5 bg-slate-700 border border-white/10 rounded-xl text-xs text-slate-300">
            <X className="h-3.5 w-3.5" /> Clear
          </button>
        )}
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-white/10 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-[11px] font-bold text-slate-500 uppercase tracking-widest">
                <th className="text-left py-3.5 px-4">Startup</th>
                <th className="text-left py-3.5 px-4 hidden md:table-cell">Owner</th>
                <th className="text-left py-3.5 px-4">Score</th>
                <th className="text-left py-3.5 px-4">Success %</th>
                <th className="text-left py-3.5 px-4">Risk</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">ROI %</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">Competition</th>
                <th className="text-left py-3.5 px-4 hidden xl:table-cell">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 8 }).map((_, j) => (
                      <td key={j} className="py-4 px-4"><div className="h-4 bg-slate-800 rounded animate-pulse" /></td>
                    ))}
                  </tr>
                ))
              ) : items.length === 0 ? (
                <tr><td colSpan={8} className="py-16 text-center text-slate-500 text-sm">No predictions found.</td></tr>
              ) : (
                items.map((p: any) => (
                  <tr key={p.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4">
                      <p className="font-semibold text-white">{p.startup_name}</p>
                    </td>
                    <td className="py-3.5 px-4 hidden md:table-cell">
                      <span className="text-xs text-slate-400">{p.owner_name}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-white">{p.business_score?.toFixed(1)}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-sm font-semibold text-green-400">{p.success_probability?.toFixed(1)}%</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        p.risk_level === 'Low' ? 'bg-green-500/10 text-green-400 border-green-500/30' :
                        p.risk_level === 'High' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                        'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}>
                        {p.risk_level}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 hidden lg:table-cell">
                      <span className="text-xs text-cyan-400">{p.estimated_roi?.toFixed(1)}%</span>
                    </td>
                    <td className="py-3.5 px-4 hidden lg:table-cell">
                      <span className="text-xs text-slate-400">{p.competition_score?.toFixed(1)}</span>
                    </td>
                    <td className="py-3.5 px-4 hidden xl:table-cell">
                      <span className="text-xs text-slate-500">{new Date(p.created_at).toLocaleDateString()}</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {!isLoading && items.length > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-white/10">
            <span className="text-xs text-slate-500">Page {page} of {pages} · {total} total</span>
            <div className="flex items-center gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1} className="p-1.5 rounded-lg bg-slate-800 disabled:opacity-30 text-slate-400"><ChevronLeft className="h-4 w-4" /></button>
              <button onClick={() => setPage(p => Math.min(pages, p + 1))} disabled={page >= pages} className="p-1.5 rounded-lg bg-slate-800 disabled:opacity-30 text-slate-400"><ChevronRight className="h-4 w-4" /></button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
