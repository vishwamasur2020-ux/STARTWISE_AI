/**
 * STARTWISE AI — Admin Users Page (Stage 12)
 * Full user management with search, filters, pagination, and CRUD actions.
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, UserCheck, UserX, ShieldCheck, ShieldOff,
  Trash2, Eye, ChevronLeft, ChevronRight, X,
} from 'lucide-react'
import {
  useAdminUsers, useUpdateUserStatus, useUpdateUserRole, useDeleteUser,
} from '@/hooks/useAdmin'

interface ConfirmDialog {
  type: 'activate' | 'deactivate' | 'role' | 'delete'
  userId: string
  userName: string
  extra?: string
}

function Badge({ role }: { role: string }) {
  const isAdmin = role.toLowerCase() === 'admin'
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${
      isAdmin
        ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
        : 'bg-slate-700 text-slate-300 border-white/10'
    }`}>
      {isAdmin && <ShieldCheck className="h-2.5 w-2.5" />}
      {role.toUpperCase()}
    </span>
  )
}

function StatusBadge({ active }: { active: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${
      active
        ? 'bg-green-500/10 text-green-400 border-green-500/30'
        : 'bg-red-500/10 text-red-400 border-red-500/30'
    }`}>
      <span className={`h-1.5 w-1.5 rounded-full ${active ? 'bg-green-400' : 'bg-red-400'}`} />
      {active ? 'Active' : 'Inactive'}
    </span>
  )
}

export default function AdminUsersPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [activeFilter, setActiveFilter] = useState<boolean | undefined>(undefined)
  const [verifiedFilter, setVerifiedFilter] = useState<boolean | undefined>(undefined)
  const [confirm, setConfirm] = useState<ConfirmDialog | null>(null)

  const params = {
    page,
    per_page: 20,
    search: search || undefined,
    role: roleFilter || undefined,
    is_active: activeFilter,
    is_verified: verifiedFilter,
  }

  const { data, isLoading } = useAdminUsers(params)
  const updateStatus = useUpdateUserStatus()
  const updateRole = useUpdateUserRole()
  const deleteUser = useDeleteUser()

  const users = (data as any)?.items ?? []
  const total = (data as any)?.total ?? 0
  const pages = (data as any)?.pages ?? 1

  function handleConfirm() {
    if (!confirm) return
    if (confirm.type === 'activate') {
      updateStatus.mutate({ id: confirm.userId, is_active: true })
    } else if (confirm.type === 'deactivate') {
      updateStatus.mutate({ id: confirm.userId, is_active: false })
    } else if (confirm.type === 'role') {
      updateRole.mutate({ id: confirm.userId, role: confirm.extra! })
    } else if (confirm.type === 'delete') {
      deleteUser.mutate(confirm.userId)
    }
    setConfirm(null)
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-white">User Management</h1>
        <p className="text-sm text-slate-400 mt-1">{total} registered users</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1) }}
            placeholder="Search name, email, ID…"
            className="w-full pl-9 pr-4 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500/40 transition-all"
          />
        </div>

        {/* Role filter */}
        <select
          value={roleFilter}
          onChange={e => { setRoleFilter(e.target.value); setPage(1) }}
          className="px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/40"
        >
          <option value="">All Roles</option>
          <option value="user">USER</option>
          <option value="admin">ADMIN</option>
        </select>

        {/* Status filter */}
        <select
          value={activeFilter === undefined ? '' : activeFilter.toString()}
          onChange={e => { setActiveFilter(e.target.value === '' ? undefined : e.target.value === 'true'); setPage(1) }}
          className="px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/40"
        >
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>

        {/* Verified filter */}
        <select
          value={verifiedFilter === undefined ? '' : verifiedFilter.toString()}
          onChange={e => { setVerifiedFilter(e.target.value === '' ? undefined : e.target.value === 'true'); setPage(1) }}
          className="px-3 py-2.5 bg-slate-800 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/40"
        >
          <option value="">All Verification</option>
          <option value="true">Verified</option>
          <option value="false">Unverified</option>
        </select>

        {(search || roleFilter || activeFilter !== undefined || verifiedFilter !== undefined) && (
          <button
            onClick={() => { setSearch(''); setRoleFilter(''); setActiveFilter(undefined); setVerifiedFilter(undefined); setPage(1) }}
            className="flex items-center gap-1.5 px-3 py-2.5 bg-slate-700 border border-white/10 rounded-xl text-xs text-slate-300 hover:text-white transition-colors"
          >
            <X className="h-3.5 w-3.5" /> Clear
          </button>
        )}
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-white/10 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm" role="table" aria-label="Users table">
            <thead>
              <tr className="border-b border-white/10 text-[11px] font-bold text-slate-500 uppercase tracking-widest">
                <th className="text-left py-3.5 px-4">User</th>
                <th className="text-left py-3.5 px-4">Role</th>
                <th className="text-left py-3.5 px-4">Status</th>
                <th className="text-left py-3.5 px-4">Email Verified</th>
                <th className="text-left py-3.5 px-4 hidden md:table-cell">Startups</th>
                <th className="text-left py-3.5 px-4 hidden lg:table-cell">Joined</th>
                <th className="text-right py-3.5 px-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 7 }).map((_, j) => (
                      <td key={j} className="py-4 px-4">
                        <div className="h-4 bg-slate-800 rounded animate-pulse w-full" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center text-slate-500 text-sm">
                    No users found.
                  </td>
                </tr>
              ) : (
                users.map((u: any) => (
                  <tr key={u.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                          {u.full_name?.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2) || 'U'}
                        </div>
                        <div className="min-w-0">
                          <p className="font-semibold text-white truncate">{u.full_name}</p>
                          <p className="text-xs text-slate-500 truncate">{u.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4"><Badge role={u.role} /></td>
                    <td className="py-3.5 px-4"><StatusBadge active={u.is_active} /></td>
                    <td className="py-3.5 px-4">
                      <div>
                        <span className={`text-xs font-semibold ${u.email_verified ?? u.is_verified ? 'text-green-400' : 'text-slate-500'}`}>
                          {u.email_verified ?? u.is_verified ? '✓ Verified' : '— Unverified'}
                        </span>
                        {u.email_verified_at && (
                          <p className="text-[10px] text-slate-500">
                            {new Date(u.email_verified_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 hidden md:table-cell">
                      <span className="text-slate-400 text-xs">{u.startup_count}</span>
                    </td>
                    <td className="py-3.5 px-4 hidden lg:table-cell">
                      <span className="text-slate-500 text-xs">
                        {new Date(u.created_at).toLocaleDateString()}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Link
                          to={`/admin/users/${u.id}`}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
                          title="View details"
                        >
                          <Eye className="h-3.5 w-3.5" />
                        </Link>
                        <button
                          onClick={() => setConfirm({
                            type: u.is_active ? 'deactivate' : 'activate',
                            userId: u.id,
                            userName: u.full_name,
                          })}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-amber-400 transition-colors"
                          title={u.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {u.is_active ? <UserX className="h-3.5 w-3.5" /> : <UserCheck className="h-3.5 w-3.5" />}
                        </button>
                        <button
                          onClick={() => setConfirm({
                            type: 'role',
                            userId: u.id,
                            userName: u.full_name,
                            extra: u.role.toLowerCase() === 'admin' ? 'user' : 'admin',
                          })}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-cyan-400 transition-colors"
                          title={u.role.toLowerCase() === 'admin' ? 'Demote to User' : 'Promote to Admin'}
                        >
                          {u.role.toLowerCase() === 'admin' ? <ShieldOff className="h-3.5 w-3.5" /> : <ShieldCheck className="h-3.5 w-3.5" />}
                        </button>
                        <button
                          onClick={() => setConfirm({ type: 'delete', userId: u.id, userName: u.full_name })}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-red-900/50 text-slate-400 hover:text-red-400 transition-colors"
                          title="Delete user"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {!isLoading && users.length > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-white/10">
            <span className="text-xs text-slate-500">
              Page {page} of {pages} · {total} total users
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-1.5 rounded-lg bg-slate-800 disabled:opacity-30 hover:bg-slate-700 text-slate-400 transition-colors"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                onClick={() => setPage(p => Math.min(pages, p + 1))}
                disabled={page >= pages}
                className="p-1.5 rounded-lg bg-slate-800 disabled:opacity-30 hover:bg-slate-700 text-slate-400 transition-colors"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      <AnimatePresence>
        {confirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setConfirm(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={e => e.stopPropagation()}
              className="bg-slate-900 border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-2xl"
            >
              <h3 className="text-lg font-bold text-white mb-2">
                {confirm.type === 'delete' ? '⚠️ Delete User' :
                 confirm.type === 'deactivate' ? 'Deactivate User?' :
                 confirm.type === 'activate' ? 'Activate User?' :
                 `Change Role to ${confirm.extra?.toUpperCase()}?`}
              </h3>
              <p className="text-sm text-slate-400 mb-6">
                {confirm.type === 'delete'
                  ? `This will permanently delete "${confirm.userName}" and all their data. This action cannot be undone.`
                  : confirm.type === 'deactivate'
                  ? `"${confirm.userName}" will be unable to log in.`
                  : confirm.type === 'activate'
                  ? `"${confirm.userName}" will regain access to their account.`
                  : `"${confirm.userName}" will be changed to ${confirm.extra?.toUpperCase()} role.`}
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setConfirm(null)}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm font-semibold text-slate-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirm}
                  className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-bold transition-colors ${
                    confirm.type === 'delete'
                      ? 'bg-red-600 hover:bg-red-500 text-white'
                      : 'bg-amber-500 hover:bg-amber-400 text-slate-900'
                  }`}
                >
                  Confirm
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
