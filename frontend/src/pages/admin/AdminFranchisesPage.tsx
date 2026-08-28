/**
 * STARTWISE AI — Admin Franchises Management Page (Stage 12)
 * Full CRUD: create, edit, delete, activate/deactivate with confirmation dialogs.
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Plus, Edit2, Trash2, ToggleLeft, ToggleRight, ChevronLeft, ChevronRight, X, AlertTriangle } from 'lucide-react'
import {
  useAdminFranchises, useCreateFranchise, useUpdateFranchise,
  useDeleteFranchise, useToggleFranchiseStatus,
} from '@/hooks/useAdmin'

type FormData = Record<string, unknown>

const EMPTY_FORM: FormData = {
  franchise_name: '', industry: '', business_model: 'Franchise',
  minimum_investment: '', maximum_investment: '', roi: '',
  risk_level: 'Medium', city: '', state: '', country: 'India',
  experience_required: 0, market_demand: 5, target_customer: '',
  description: '', website: '', contact_email: '', logo_url: '', is_active: true,
}

interface ConfirmState { type: 'delete' | 'toggle'; id: string; name: string; active?: boolean }

export default function AdminFranchisesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isActiveFilter, setIsActiveFilter] = useState<boolean | undefined>(undefined)
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [form, setForm] = useState<FormData>(EMPTY_FORM)
  const [confirm, setConfirm] = useState<ConfirmState | null>(null)
  const [formError, setFormError] = useState('')

  const params = { page, per_page: 20, search: search || undefined, is_active: isActiveFilter }
  const { data, isLoading } = useAdminFranchises(params)
  const create = useCreateFranchise()
  const update = useUpdateFranchise()
  const deleteFranchise = useDeleteFranchise()
  const toggleStatus = useToggleFranchiseStatus()

  const items = (data as any)?.items ?? []
  const total = (data as any)?.total ?? 0
  const pages = (data as any)?.pages ?? 1

  function openCreate() {
    setForm(EMPTY_FORM)
    setEditId(null)
    setFormError('')
    setShowForm(true)
  }

  function openEdit(f: any) {
    setForm({ ...f })
    setEditId(f.id)
    setFormError('')
    setShowForm(true)
  }

  function validateForm(): boolean {
    const minInv = Number(form.minimum_investment)
    const maxInv = Number(form.maximum_investment)
    const roi = Number(form.roi)
    if (!form.franchise_name) { setFormError('Franchise name is required.'); return false }
    if (!form.industry) { setFormError('Industry is required.'); return false }
    if (minInv <= 0) { setFormError('Minimum investment must be > 0.'); return false }
    if (maxInv < minInv) { setFormError('Maximum investment must be ≥ minimum.'); return false }
    if (roi < 0) { setFormError('ROI must be ≥ 0.'); return false }
    setFormError('')
    return true
  }

  async function handleSubmit() {
    if (!validateForm()) return
    const payload = {
      ...form,
      minimum_investment: Number(form.minimum_investment),
      maximum_investment: Number(form.maximum_investment),
      roi: Number(form.roi),
      experience_required: Number(form.experience_required),
      market_demand: Number(form.market_demand),
    }
    if (editId) {
      await update.mutateAsync({ id: editId, data: payload })
    } else {
      await create.mutateAsync(payload)
    }
    setShowForm(false)
  }

  function handleConfirm() {
    if (!confirm) return
    if (confirm.type === 'delete') deleteFranchise.mutate(confirm.id)
    else toggleStatus.mutate({ id: confirm.id, is_active: !confirm.active })
    setConfirm(null)
  }

  const field = (key: string, label: string, type = 'text', required = false) => (
    <div>
      <label className="block text-xs font-semibold text-slate-400 mb-1.5">{label}{required && <span className="text-red-400 ml-1">*</span>}</label>
      <input
        type={type}
        value={form[key] as string ?? ''}
        onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        className="w-full px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/40 transition-all"
      />
    </div>
  )

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-black text-white">Franchise Management</h1>
          <p className="text-sm text-slate-400 mt-1">{total} franchises</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl text-sm font-bold text-slate-900 hover:opacity-90 transition-opacity"
        >
          <Plus className="h-4 w-4" /> Add Franchise
        </button>
      </div>

      {/* Demo data notice */}
      <div className="flex items-center gap-2 px-4 py-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-400">
        <AlertTriangle className="h-4 w-4 flex-shrink-0" />
        <span><strong>Demo / Synthetic Data</strong> — Franchise records are for demonstration purposes. Do not represent as verified financial data.</span>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input value={search} onChange={e => { setSearch(e.target.value); setPage(1) }} placeholder="Search franchise…" className="w-full pl-9 pr-4 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40" />
        </div>
        <select value={isActiveFilter === undefined ? '' : isActiveFilter.toString()} onChange={e => { setIsActiveFilter(e.target.value === '' ? undefined : e.target.value === 'true'); setPage(1) }} className="px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
        {(search || isActiveFilter !== undefined) && (
          <button onClick={() => { setSearch(''); setIsActiveFilter(undefined); setPage(1) }} className="flex items-center gap-1.5 px-3 py-2.5 bg-slate-700 border border-white/10 rounded-xl text-xs text-slate-300"><X className="h-3.5 w-3.5" /> Clear</button>
        )}
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-white/10 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-[11px] font-bold text-slate-500 uppercase tracking-widest">
                <th className="text-left py-3.5 px-4">Franchise</th>
                <th className="text-left py-3.5 px-4 hidden sm:table-cell">Industry</th>
                <th className="text-left py-3.5 px-4 hidden md:table-cell">Investment</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">ROI</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">Risk</th>
                <th className="text-left py-3.5 px-4">Status</th>
                <th className="text-right py-3.5 px-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>{Array.from({ length: 7 }).map((_, j) => <td key={j} className="py-4 px-4"><div className="h-4 bg-slate-800 rounded animate-pulse" /></td>)}</tr>
                ))
              ) : items.length === 0 ? (
                <tr><td colSpan={7} className="py-16 text-center text-slate-500 text-sm">No franchises found.</td></tr>
              ) : (
                items.map((f: any) => (
                  <tr key={f.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="py-3.5 px-4">
                      <p className="font-semibold text-white">{f.franchise_name}</p>
                      <p className="text-xs text-slate-500">{f.city}{f.city && f.country ? ', ' : ''}{f.country}</p>
                    </td>
                    <td className="py-3.5 px-4 hidden sm:table-cell"><span className="text-xs text-slate-400">{f.industry}</span></td>
                    <td className="py-3.5 px-4 hidden md:table-cell"><span className="text-xs text-slate-400">₹{f.minimum_investment?.toLocaleString('en-IN')} – {f.maximum_investment?.toLocaleString('en-IN')}</span></td>
                    <td className="py-3.5 px-4 hidden lg:table-cell"><span className="text-xs text-green-400 font-semibold">{f.roi}%</span></td>
                    <td className="py-3.5 px-4 hidden lg:table-cell">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        f.risk_level === 'Low' ? 'bg-green-500/10 text-green-400 border-green-500/30' :
                        f.risk_level === 'High' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                        'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}>{f.risk_level}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${f.is_active ? 'bg-green-500/10 text-green-400 border-green-500/30' : 'bg-slate-700 text-slate-500 border-white/10'}`}>
                        {f.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => openEdit(f)} className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"><Edit2 className="h-3.5 w-3.5" /></button>
                        <button onClick={() => setConfirm({ type: 'toggle', id: f.id, name: f.franchise_name, active: f.is_active })} className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-amber-400 transition-colors">
                          {f.is_active ? <ToggleRight className="h-3.5 w-3.5" /> : <ToggleLeft className="h-3.5 w-3.5" />}
                        </button>
                        <button onClick={() => setConfirm({ type: 'delete', id: f.id, name: f.franchise_name })} className="p-1.5 rounded-lg bg-slate-800 hover:bg-red-900/50 text-slate-400 hover:text-red-400 transition-colors"><Trash2 className="h-3.5 w-3.5" /></button>
                      </div>
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

      {/* Form Modal */}
      <AnimatePresence>
        {showForm && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto" onClick={() => setShowForm(false)}>
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} onClick={e => e.stopPropagation()} className="bg-slate-900 border border-white/10 rounded-2xl p-6 w-full max-w-2xl shadow-2xl my-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white">{editId ? 'Edit Franchise' : 'Create Franchise'}</h3>
                <button onClick={() => setShowForm(false)} className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 transition-colors"><X className="h-4 w-4" /></button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {field('franchise_name', 'Franchise Name', 'text', true)}
                {field('industry', 'Industry', 'text', true)}
                {field('business_model', 'Business Model')}
                {field('minimum_investment', 'Min Investment (₹)', 'number', true)}
                {field('maximum_investment', 'Max Investment (₹)', 'number', true)}
                {field('roi', 'Expected ROI %', 'number', true)}
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1.5">Risk Level <span className="text-red-400">*</span></label>
                  <select value={form.risk_level as string} onChange={e => setForm(f => ({ ...f, risk_level: e.target.value }))} className="w-full px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none">
                    <option>Low</option><option>Medium</option><option>High</option>
                  </select>
                </div>
                {field('city', 'City')}
                {field('state', 'State')}
                {field('country', 'Country')}
                {field('experience_required', 'Experience Required (years)', 'number')}
                {field('market_demand', 'Market Demand (1–10)', 'number')}
                {field('target_customer', 'Target Customer')}
                {field('website', 'Website URL')}
                {field('contact_email', 'Contact Email', 'email')}
                {field('logo_url', 'Logo URL')}
              </div>
              <div className="mt-4">
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Description</label>
                <textarea value={form.description as string ?? ''} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={3} className="w-full px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none resize-none" />
              </div>
              <div className="flex items-center gap-3 mt-4">
                <input id="franchise-active" type="checkbox" checked={form.is_active as boolean} onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))} className="w-4 h-4 rounded" />
                <label htmlFor="franchise-active" className="text-sm text-slate-300 font-semibold">Active</label>
              </div>
              {formError && <p className="text-xs text-red-400 mt-3">{formError}</p>}
              <div className="flex gap-3 mt-6">
                <button onClick={() => setShowForm(false)} className="flex-1 py-2.5 rounded-xl bg-slate-800 text-sm font-semibold text-slate-300 hover:bg-slate-700 transition-colors">Cancel</button>
                <button onClick={handleSubmit} disabled={create.isPending || update.isPending} className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-sm font-bold text-slate-900 hover:opacity-90 transition-opacity disabled:opacity-50">
                  {editId ? 'Update Franchise' : 'Create Franchise'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confirm Modal */}
      <AnimatePresence>
        {confirm && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setConfirm(null)}>
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} onClick={e => e.stopPropagation()} className="bg-slate-900 border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-2xl">
              <h3 className="text-lg font-bold text-white mb-2">
                {confirm.type === 'delete' ? '⚠️ Delete Franchise' : confirm.active ? 'Deactivate Franchise?' : 'Activate Franchise?'}
              </h3>
              <p className="text-sm text-slate-400 mb-6">
                {confirm.type === 'delete' ? `Permanently delete "${confirm.name}"? This cannot be undone.` : `${confirm.active ? 'Deactivate' : 'Activate'} "${confirm.name}"?`}
              </p>
              <div className="flex gap-3">
                <button onClick={() => setConfirm(null)} className="flex-1 py-2.5 px-4 rounded-xl bg-slate-800 text-sm font-semibold text-slate-300">Cancel</button>
                <button onClick={handleConfirm} className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-bold ${confirm.type === 'delete' ? 'bg-red-600 hover:bg-red-500 text-white' : 'bg-amber-500 hover:bg-amber-400 text-slate-900'}`}>Confirm</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
