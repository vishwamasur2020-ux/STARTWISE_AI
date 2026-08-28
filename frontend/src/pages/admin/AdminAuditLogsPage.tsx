/**
 * STARTWISE AI — Admin Audit Logs Page (Stage 12)
 */

import { useState } from 'react'
import { ChevronLeft, ChevronRight, X, Filter } from 'lucide-react'
import { useAdminAuditLogs } from '@/hooks/useAdmin'

const ACTION_BADGES: Record<string, string> = {
  USER_ACTIVATED: 'bg-green-500/10 text-green-400 border-green-500/30',
  USER_DEACTIVATED: 'bg-red-500/10 text-red-400 border-red-500/30',
  USER_DELETED: 'bg-red-500/10 text-red-400 border-red-500/30',
  USER_ROLE_CHANGED: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  USER_VIEWED: 'bg-slate-700 text-slate-400 border-white/10',
  FRANCHISE_CREATED: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  FRANCHISE_UPDATED: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  FRANCHISE_DELETED: 'bg-red-500/10 text-red-400 border-red-500/30',
  FRANCHISE_ACTIVATED: 'bg-green-500/10 text-green-400 border-green-500/30',
  FRANCHISE_DEACTIVATED: 'bg-red-500/10 text-red-400 border-red-500/30',
  STARTUP_VIEWED: 'bg-slate-700 text-slate-400 border-white/10',
  REPORT_DELETED: 'bg-red-500/10 text-red-400 border-red-500/30',
  MARKETING_DELETED: 'bg-red-500/10 text-red-400 border-red-500/30',
}

export default function AdminAuditLogsPage() {
  const [page, setPage] = useState(1)
  const [actionFilter, setActionFilter] = useState('')
  const [resourceFilter, setResourceFilter] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const params = {
    page, per_page: 50,
    action: actionFilter || undefined,
    resource: resourceFilter || undefined,
    start_date: startDate || undefined,
    end_date: endDate || undefined,
  }
  const { data, isLoading } = useAdminAuditLogs(params)
  const items = (data as any)?.items ?? []
  const total = (data as any)?.total ?? 0
  const pages = (data as any)?.pages ?? 1

  function clearFilters() {
    setActionFilter(''); setResourceFilter(''); setStartDate(''); setEndDate(''); setPage(1)
  }
  const hasFilters = actionFilter || resourceFilter || startDate || endDate

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-black text-white">Audit Logs</h1>
        <p className="text-sm text-slate-400 mt-1">{total} audit events recorded</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative min-w-[180px]">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
          <input value={actionFilter} onChange={e => { setActionFilter(e.target.value); setPage(1) }} placeholder="Filter action…" className="w-full pl-8 pr-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40" />
        </div>
        <div className="relative min-w-[160px]">
          <input value={resourceFilter} onChange={e => { setResourceFilter(e.target.value); setPage(1) }} placeholder="Filter resource…" className="w-full px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40" />
        </div>
        <div className="flex items-center gap-2">
          <input type="date" value={startDate} onChange={e => { setStartDate(e.target.value); setPage(1) }} className="px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-amber-500/40" />
          <span className="text-slate-600 text-xs">to</span>
          <input type="date" value={endDate} onChange={e => { setEndDate(e.target.value); setPage(1) }} className="px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-amber-500/40" />
        </div>
        {hasFilters && (
          <button onClick={clearFilters} className="flex items-center gap-1.5 px-3 py-2.5 bg-slate-700 border border-white/10 rounded-xl text-xs text-slate-300"><X className="h-3.5 w-3.5" /> Clear</button>
        )}
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-white/10 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-[11px] font-bold text-slate-500 uppercase tracking-widest">
                <th className="text-left py-3.5 px-4">Timestamp</th>
                <th className="text-left py-3.5 px-4">Admin</th>
                <th className="text-left py-3.5 px-4">Action</th>
                <th className="text-left py-3.5 px-4 hidden sm:table-cell">Resource</th>
                <th className="text-left py-3.5 px-4 hidden md:table-cell">Resource ID</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">IP Address</th>
                <th className="text-left py-3.5 px-4 hidden xl:table-cell">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => <tr key={i}>{Array.from({ length: 7 }).map((_, j) => <td key={j} className="py-4 px-4"><div className="h-4 bg-slate-800 rounded animate-pulse" /></td>)}</tr>)
              ) : items.length === 0 ? (
                <tr><td colSpan={7} className="py-16 text-center text-slate-500 text-sm">No audit logs found.</td></tr>
              ) : (
                items.map((log: any) => (
                  <tr key={log.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 px-4">
                      <p className="text-xs text-slate-300 font-mono">{new Date(log.timestamp).toLocaleString()}</p>
                    </td>
                    <td className="py-3 px-4">
                      <p className="text-xs text-white font-semibold">{log.admin_name || 'System'}</p>
                      <p className="text-[10px] text-slate-500">{log.admin_email || ''}</p>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border whitespace-nowrap ${ACTION_BADGES[log.action] || 'bg-slate-700 text-slate-400 border-white/10'}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 hidden sm:table-cell">
                      <span className="text-xs text-slate-400 capitalize">{log.resource?.replace('_', ' ')}</span>
                    </td>
                    <td className="py-3 px-4 hidden md:table-cell">
                      <span className="text-[10px] font-mono text-slate-500 truncate max-w-[120px] block">{log.resource_id || '—'}</span>
                    </td>
                    <td className="py-3 px-4 hidden lg:table-cell">
                      <span className="text-[10px] font-mono text-slate-500">{log.ip_address || '—'}</span>
                    </td>
                    <td className="py-3 px-4 hidden xl:table-cell">
                      {log.details && Object.keys(log.details).length > 0 ? (
                        <span className="text-[10px] text-slate-500 truncate max-w-[160px] block">{JSON.stringify(log.details).slice(0, 80)}</span>
                      ) : <span className="text-slate-600">—</span>}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {!isLoading && items.length > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-white/10">
            <span className="text-xs text-slate-500">Page {page} of {pages} · {total} total events</span>
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
