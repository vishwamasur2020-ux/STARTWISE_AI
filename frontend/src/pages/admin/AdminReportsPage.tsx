/**
 * STARTWISE AI — Admin Reports Page (Stage 12)
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Trash2, ChevronLeft, ChevronRight, X, FileText, CheckCircle2 } from 'lucide-react'
import { useAdminReports, useDeleteReport } from '@/hooks/useAdmin'

interface Confirm { id: string; title: string }

export default function AdminReportsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [confirm, setConfirm] = useState<Confirm | null>(null)

  const params = { page, per_page: 20, search: search || undefined }
  const { data, isLoading } = useAdminReports(params)
  const deleteReport = useDeleteReport()

  const items = (data as any)?.items ?? []
  const total = (data as any)?.total ?? 0
  const pages = (data as any)?.pages ?? 1

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-black text-white">Report Management</h1>
        <p className="text-sm text-slate-400 mt-1">{total} PDF reports generated</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input value={search} onChange={e => { setSearch(e.target.value); setPage(1) }} placeholder="Search by title, user email…" className="w-full pl-9 pr-4 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40" />
        </div>
        {search && <button onClick={() => { setSearch(''); setPage(1) }} className="flex items-center gap-1.5 px-3 py-2.5 bg-slate-700 border border-white/10 rounded-xl text-xs text-slate-300"><X className="h-3.5 w-3.5" /> Clear</button>}
      </div>

      <div className="bg-slate-900 border border-white/10 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-[11px] font-bold text-slate-500 uppercase tracking-widest">
                <th className="text-left py-3.5 px-4">Report</th>
                <th className="text-left py-3.5 px-4 hidden md:table-cell">Owner</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">Startup</th>
                <th className="text-left py-3.5 px-4 hidden sm:table-cell">Generated</th>
                <th className="text-left py-3.5 px-4">File</th>
                <th className="text-right py-3.5 px-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => <tr key={i}>{Array.from({ length: 6 }).map((_, j) => <td key={j} className="py-4 px-4"><div className="h-4 bg-slate-800 rounded animate-pulse" /></td>)}</tr>)
              ) : items.length === 0 ? (
                <tr><td colSpan={6} className="py-16 text-center text-slate-500 text-sm">No reports found.</td></tr>
              ) : (
                items.map((r: any) => (
                  <tr key={r.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-rose-400 flex-shrink-0" />
                        <span className="font-semibold text-white truncate max-w-[200px]">{r.title}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 hidden md:table-cell">
                      <p className="text-xs text-slate-300">{r.owner_name}</p>
                      <p className="text-xs text-slate-500">{r.owner_email}</p>
                    </td>
                    <td className="py-3.5 px-4 hidden lg:table-cell"><span className="text-xs text-slate-400">{r.startup_name || '—'}</span></td>
                    <td className="py-3.5 px-4 hidden sm:table-cell"><span className="text-xs text-slate-500">{new Date(r.generated_at).toLocaleDateString()}</span></td>
                    <td className="py-3.5 px-4">
                      {r.has_file ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-green-400"><CheckCircle2 className="h-3 w-3" /> Available</span>
                      ) : (
                        <span className="text-[10px] font-bold text-slate-600">No file</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setConfirm({ id: r.id, title: r.title })}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-red-900/50 text-slate-400 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
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

      <AnimatePresence>
        {confirm && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setConfirm(null)}>
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} onClick={e => e.stopPropagation()} className="bg-slate-900 border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-2xl">
              <h3 className="text-lg font-bold text-white mb-2">⚠️ Delete Report?</h3>
              <p className="text-sm text-slate-400 mb-6">Delete report "{confirm.title}"? This cannot be undone.</p>
              <div className="flex gap-3">
                <button onClick={() => setConfirm(null)} className="flex-1 py-2.5 rounded-xl bg-slate-800 text-sm font-semibold text-slate-300">Cancel</button>
                <button onClick={() => { deleteReport.mutate(confirm.id); setConfirm(null) }} className="flex-1 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-sm font-bold text-white">Delete</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
