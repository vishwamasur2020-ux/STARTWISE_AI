/**
 * STARTWISE AI — Admin User Detail Page (Stage 12)
 */

import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Building2, TrendingUp, FileText, ShieldCheck, Calendar } from 'lucide-react'
import { useAdminUser } from '@/hooks/useAdmin'

export default function AdminUserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: user, isLoading } = useAdminUser(id ?? '')

  if (isLoading) {
    return (
      <div className="space-y-6 pb-12">
        <div className="h-8 bg-slate-800 rounded w-48 animate-pulse" />
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-6 animate-pulse space-y-4">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="h-4 bg-slate-800 rounded w-full" />)}
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="text-center py-20">
        <p className="text-slate-400">User not found.</p>
        <Link to="/admin/users" className="text-amber-400 text-sm mt-2 inline-block">← Back to Users</Link>
      </div>
    )
  }

  const u = user as any
  const roleLower = (u.role || '').toLowerCase()

  return (
    <div className="space-y-6 pb-12">
      <Link to="/admin/users" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to Users
      </Link>

      {/* Profile Header */}
      <div className="bg-slate-900 border border-white/10 rounded-2xl p-6">
        <div className="flex items-start gap-5 flex-wrap">
          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white text-xl font-black flex-shrink-0">
            {u.full_name?.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2) || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-black text-white">{u.full_name}</h1>
              {roleLower === 'admin' && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
                  <ShieldCheck className="h-3 w-3" /> ADMIN
                </span>
              )}
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold border ${
                u.is_active ? 'bg-green-500/10 text-green-400 border-green-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'
              }`}>
                <span className={`h-1.5 w-1.5 rounded-full ${u.is_active ? 'bg-green-400' : 'bg-red-400'}`} />
                {u.is_active ? 'Active' : 'Inactive'}
              </span>

              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold border ${
                u.email_verified ?? u.is_verified ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-slate-700 text-slate-400 border-white/10'
              }`}>
                {u.email_verified ?? u.is_verified ? '✓ Email Verified' : '— Unverified'}
              </span>

              {u.email_verified_at && (
                <span className="text-xs text-slate-400">
                  Verified: {new Date(u.email_verified_at).toLocaleDateString()}
                </span>
              )}
            </div>
            <p className="text-slate-400 mt-1">{u.email}</p>
            {u.phone && <p className="text-slate-500 text-sm">{u.phone}</p>}
            {u.location && <p className="text-slate-500 text-sm">{u.location}</p>}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Startups', value: u.startup_count ?? 0, icon: Building2, color: 'text-indigo-400' },
          { label: 'AI Analyses', value: u.analysis_count ?? 0, icon: TrendingUp, color: 'text-green-400' },
          { label: 'Reports', value: u.report_count ?? 0, icon: FileText, color: 'text-rose-400' },
          { label: 'Member Since', value: new Date(u.created_at).toLocaleDateString('en-IN'), icon: Calendar, color: 'text-amber-400' },
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

      {/* Recent Startups */}
      {u.recent_startups?.length > 0 && (
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-6">
          <h3 className="text-sm font-bold text-white mb-4">Recent Startups</h3>
          <div className="space-y-2">
            {u.recent_startups.map((s: any) => (
              <div key={s.id} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                <span className="text-sm font-semibold text-slate-200">{s.business_name}</span>
                <span className="text-xs text-slate-500">{new Date(s.created_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Reports */}
      {u.recent_reports?.length > 0 && (
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-6">
          <h3 className="text-sm font-bold text-white mb-4">Recent Reports</h3>
          <div className="space-y-2">
            {u.recent_reports.map((r: any) => (
              <div key={r.id} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                <span className="text-sm font-semibold text-slate-200">{r.title}</span>
                <span className="text-xs text-slate-500">{new Date(r.generated_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
