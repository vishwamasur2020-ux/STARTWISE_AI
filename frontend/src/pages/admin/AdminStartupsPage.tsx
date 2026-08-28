/**
 * STARTWISE AI — Admin Startups Page (Stage 12)
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Eye, ChevronLeft, ChevronRight, X } from 'lucide-react'
import { useAdminStartups } from '@/hooks/useAdmin'

const RISK_COLORS: Record<string, string> = {
  Low: 'bg-green-500/10 text-green-400 border-green-500/30',
  Medium: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  High: 'bg-red-500/10 text-red-400 border-red-500/30',
}

const CATEGORIES = ['Technology', 'Food', 'Retail', 'Healthcare', 'Education', 'Agriculture', 'Manufacturing', 'Finance', 'Tourism', 'Other']

export default function AdminStartupsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [riskLevel, setRiskLevel] = useState('')

  const params = { page, per_page: 20, search: search || undefined, category: category || undefined, risk_level: riskLevel || undefined }
  const { data, isLoading } = useAdminStartups(params)
  const startups = (data as any)?.items ?? []
  const total = (data as any)?.total ?? 0
  const pages = (data as any)?.pages ?? 1

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-black text-white">Startup Management</h1>
        <p className="text-sm text-slate-400 mt-1">{total} total startups</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1) }}
            placeholder="Search startup name, location…"
            className="w-full pl-9 pr-4 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40 transition-all"
          />
        </div>
        <select
          value={category}
          onChange={e => { setCategory(e.target.value); setPage(1) }}
          className="px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none"
        >
          <option value="">All Categories</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select
          value={riskLevel}
          onChange={e => { setRiskLevel(e.target.value); setPage(1) }}
          className="px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none"
        >
          <option value="">All Risk</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
        </select>
        {(search || category || riskLevel) && (
          <button
            onClick={() => { setSearch(''); setCategory(''); setRiskLevel(''); setPage(1) }}
            className="flex items-center gap-1.5 px-3 py-2.5 bg-slate-700 border border-white/10 rounded-xl text-xs text-slate-300"
          >
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
                <th className="text-left py-3.5 px-4">Business</th>
                <th className="text-left py-3.5 px-4 hidden md:table-cell">Owner</th>
                <th className="text-left py-3.5 px-4 hidden sm:table-cell">Category</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">Investment</th>
                <th className="text-left py-3.5 px-4">Score</th>
                <th className="text-left py-3.5 px-4">Risk</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">ROI</th>
                <th className="text-right py-3.5 px-4">Actions</th>
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
              ) : startups.length === 0 ? (
                <tr><td colSpan={8} className="py-16 text-center text-slate-500 text-sm">No startups found.</td></tr>
              ) : (
                startups.map((s: any) => (
                  <tr key={s.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="py-3.5 px-4">
                      <p className="font-semibold text-white">{s.business_name}</p>
                      <p className="text-xs text-slate-500">{s.preferred_location}</p>
                    </td>
                    <td className="py-3.5 px-4 hidden md:table-cell">
                      <p className="text-slate-300 text-xs">{s.owner_name}</p>
                      <p className="text-slate-500 text-xs">{s.owner_email}</p>
                    </td>
                    <td className="py-3.5 px-4 hidden sm:table-cell">
                      <span className="text-xs text-slate-400">{s.business_category}</span>
                    </td>
                    <td className="py-3.5 px-4 hidden lg:table-cell">
                      <span className="text-xs text-slate-400">₹{s.investment_amount?.toLocaleString('en-IN')}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      {s.has_prediction ? (
                        <span className="text-sm font-bold text-white">{s.business_score?.toFixed(1)}</span>
                      ) : (
                        <span className="text-xs text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      {s.risk_level ? (
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${RISK_COLORS[s.risk_level] || 'bg-slate-700 text-slate-400 border-white/10'}`}>
                          {s.risk_level}
                        </span>
                      ) : <span className="text-xs text-slate-600">—</span>}
                    </td>
                    <td className="py-3.5 px-4 hidden lg:table-cell">
                      {s.estimated_roi != null ? (
                        <span className="text-xs text-green-400 font-semibold">{s.estimated_roi?.toFixed(1)}%</span>
                      ) : <span className="text-xs text-slate-600">—</span>}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        to={`/admin/startups/${s.id}`}
                        className="inline-flex items-center gap-1 p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {!isLoading && startups.length > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-white/10">
            <span className="text-xs text-slate-500">Page {page} of {pages} · {total} total</span>
            <div className="flex items-center gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1} className="p-1.5 rounded-lg bg-slate-800 disabled:opacity-30 hover:bg-slate-700 text-slate-400">
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button onClick={() => setPage(p => Math.min(pages, p + 1))} disabled={page >= pages} className="p-1.5 rounded-lg bg-slate-800 disabled:opacity-30 hover:bg-slate-700 text-slate-400">
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
