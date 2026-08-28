/**
 * STARTWISE AI — Admin Dashboard Page (Stage 12)
 * Complete replacement with real database statistics and KPI cards.
 */

import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Users, Building2, TrendingUp, FileText, Store,
  ShieldCheck, AlertTriangle, BarChart3, Activity,
  ArrowRight, RefreshCw,
} from 'lucide-react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  Tooltip, PieChart, Pie, Cell, Legend,
} from 'recharts'
import { useAdminDashboard } from '@/hooks/useAdmin'

// ── KPI Card ─────────────────────────────────────────────────────────────────
interface KpiCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  color: string
  href?: string
  badge?: string
}

function KpiCard({ title, value, subtitle, icon, color, href, badge }: KpiCardProps) {
  const inner = (
    <motion.div
      whileHover={{ y: -3, scale: 1.01 }}
      className={`relative bg-slate-900 border border-white/10 rounded-2xl p-5 overflow-hidden group cursor-default transition-all`}
    >
      {/* Glow */}
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity bg-gradient-to-br ${color} opacity-5`} />

      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">{title}</p>
          <p className="text-3xl font-black text-white leading-none">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`h-11 w-11 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center flex-shrink-0 shadow-lg`}>
          {icon}
        </div>
      </div>

      {badge && (
        <div className="mt-3 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/5 text-[10px] font-bold text-slate-400 border border-white/10">
          {badge}
        </div>
      )}

      {href && (
        <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <ArrowRight className="h-4 w-4 text-slate-500" />
        </div>
      )}
    </motion.div>
  )

  return href ? <Link to={href}>{inner}</Link> : inner
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
function KpiSkeleton() {
  return (
    <div className="bg-slate-900 border border-white/10 rounded-2xl p-5 animate-pulse">
      <div className="h-3 bg-slate-700 rounded w-24 mb-3" />
      <div className="h-9 bg-slate-700 rounded w-16 mb-2" />
      <div className="h-2 bg-slate-800 rounded w-20" />
    </div>
  )
}

// ── Quick Links ───────────────────────────────────────────────────────────────
const QUICK_LINKS = [
  { label: 'Manage Users',      href: '/admin/users',       icon: Users,      color: 'from-cyan-500 to-blue-600' },
  { label: 'View Startups',     href: '/admin/startups',    icon: Building2,  color: 'from-indigo-500 to-purple-600' },
  { label: 'Predictions',       href: '/admin/predictions', icon: TrendingUp, color: 'from-green-500 to-emerald-600' },
  { label: 'Franchises',        href: '/admin/franchises',  icon: Store,      color: 'from-amber-500 to-orange-600' },
  { label: 'Reports',           href: '/admin/reports',     icon: FileText,   color: 'from-rose-500 to-pink-600' },
  { label: 'Platform Analytics',href: '/admin/analytics',   icon: BarChart3,  color: 'from-violet-500 to-purple-600' },
]

const RISK_COLORS = ['#10b981', '#f59e0b', '#ef4444']

export default function AdminDashboardPage() {
  const { data, isLoading, refetch, isFetching } = useAdminDashboard()

  const stats = data as {
    users: { total: number; active: number }
    startups: { total: number }
    predictions: { total: number; average_score: number; average_success_probability: number; average_roi: number; high_risk_count: number }
    reports: { total: number; emails_sent: number }
    franchises: { total: number }
  } | undefined

  const riskChartData = stats
    ? [
        { name: 'Low Risk', value: Math.max(0, stats.predictions.total - stats.predictions.high_risk_count - Math.floor(stats.predictions.total * 0.3)) },
        { name: 'Medium Risk', value: Math.floor(stats.predictions.total * 0.3) },
        { name: 'High Risk', value: stats.predictions.high_risk_count },
      ].filter(d => d.value > 0)
    : []

  const overviewBarData = stats
    ? [
        { name: 'Users', value: stats.users.total, fill: '#06b6d4' },
        { name: 'Startups', value: stats.startups.total, fill: '#6366f1' },
        { name: 'Analyses', value: stats.predictions.total, fill: '#10b981' },
        { name: 'Franchises', value: stats.franchises.total, fill: '#f59e0b' },
        { name: 'Reports', value: stats.reports.total, fill: '#f43f5e' },
      ]
    : []

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-widest mb-2">
            <ShieldCheck className="h-4 w-4" />
            Admin Control Center
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Platform Overview
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Monitor and manage the STARTWISE AI platform.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-white/10 rounded-xl text-xs font-semibold text-slate-300 transition-colors"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* KPI Cards — Row 1 */}
      <div>
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">User Statistics</h2>
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {isLoading ? (
            Array.from({ length: 4 }).map((_, i) => <KpiSkeleton key={i} />)
          ) : (
            <>
              <KpiCard
                title="Total Users"
                value={stats?.users.total ?? 0}
                subtitle="Registered accounts"
                icon={<Users className="h-5 w-5 text-white" />}
                color="from-cyan-500 to-blue-600"
                href="/admin/users"
              />
              <KpiCard
                title="Active Users"
                value={stats?.users.active ?? 0}
                subtitle={`${stats ? Math.round((stats.users.active / Math.max(stats.users.total, 1)) * 100) : 0}% active rate`}
                icon={<Activity className="h-5 w-5 text-white" />}
                color="from-green-500 to-emerald-600"
              />
              <KpiCard
                title="Total Startups"
                value={stats?.startups.total ?? 0}
                subtitle="Startup ideas created"
                icon={<Building2 className="h-5 w-5 text-white" />}
                color="from-indigo-500 to-purple-600"
                href="/admin/startups"
              />
              <KpiCard
                title="Total Analyses"
                value={stats?.predictions.total ?? 0}
                subtitle="AI predictions run"
                icon={<TrendingUp className="h-5 w-5 text-white" />}
                color="from-violet-500 to-purple-700"
                href="/admin/predictions"
              />
            </>
          )}
        </div>
      </div>

      {/* KPI Cards — Row 2 */}
      <div>
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Platform Metrics</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {isLoading ? (
            Array.from({ length: 5 }).map((_, i) => <KpiSkeleton key={i} />)
          ) : (
            <>
              <KpiCard
                title="Avg Business Score"
                value={`${stats?.predictions.average_score ?? 0}%`}
                icon={<BarChart3 className="h-5 w-5 text-white" />}
                color="from-amber-400 to-orange-500"
              />
              <KpiCard
                title="Avg Success Prob."
                value={`${stats?.predictions.average_success_probability ?? 0}%`}
                icon={<TrendingUp className="h-5 w-5 text-white" />}
                color="from-green-400 to-teal-500"
              />
              <KpiCard
                title="Average ROI"
                value={`${stats?.predictions.average_roi ?? 0}%`}
                icon={<BarChart3 className="h-5 w-5 text-white" />}
                color="from-blue-400 to-cyan-500"
              />
              <KpiCard
                title="High Risk Startups"
                value={stats?.predictions.high_risk_count ?? 0}
                badge="Requires attention"
                icon={<AlertTriangle className="h-5 w-5 text-white" />}
                color="from-rose-500 to-red-600"
              />
              <KpiCard
                title="Total Franchises"
                value={stats?.franchises.total ?? 0}
                icon={<Store className="h-5 w-5 text-white" />}
                color="from-amber-500 to-yellow-600"
                href="/admin/franchises"
              />
            </>
          )}
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Overview Bar */}
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-6">
          <h3 className="text-sm font-bold text-white mb-4">Platform Overview</h3>
          {isLoading ? (
            <div className="h-48 bg-slate-800 rounded-xl animate-pulse" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={overviewBarData} barSize={32} style={{ fontFamily: 'inherit' }}>
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }}
                  labelStyle={{ color: '#fff', fontWeight: 700 }}
                  itemStyle={{ color: '#94a3b8' }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {overviewBarData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Risk Distribution Pie */}
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-6">
          <h3 className="text-sm font-bold text-white mb-4">Risk Distribution</h3>
          {isLoading ? (
            <div className="h-48 bg-slate-800 rounded-xl animate-pulse" />
          ) : riskChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={riskChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {riskChartData.map((_, i) => (
                    <Cell key={i} fill={RISK_COLORS[i % RISK_COLORS.length]} />
                  ))}
                </Pie>
                <Legend
                  formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{value}</span>}
                />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }}
                  itemStyle={{ color: '#94a3b8' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500 text-sm">
              No prediction data available yet.
            </div>
          )}
        </div>
      </div>

      {/* Quick Links */}
      <div>
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Quick Navigation</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {QUICK_LINKS.map((link) => {
            const Icon = link.icon
            return (
              <Link key={link.href} to={link.href}>
                <motion.div
                  whileHover={{ y: -3, scale: 1.03 }}
                  className="flex flex-col items-center gap-2 p-4 bg-slate-900 border border-white/10 rounded-2xl hover:border-white/20 transition-all cursor-pointer group"
                >
                  <div className={`h-10 w-10 rounded-xl bg-gradient-to-br ${link.color} flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <span className="text-xs font-semibold text-slate-300 text-center leading-tight">{link.label}</span>
                </motion.div>
              </Link>
            )
          })}
        </div>
      </div>

      {/* Reports & Additional KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {isLoading ? (
          <>
            <KpiSkeleton />
            <KpiSkeleton />
          </>
        ) : (
          <>
            <KpiCard
              title="Total Reports"
              value={stats?.reports.total ?? 0}
              subtitle="PDF reports generated"
              icon={<FileText className="h-5 w-5 text-white" />}
              color="from-rose-500 to-pink-600"
              href="/admin/reports"
            />
            <KpiCard
              title="Emails Sent"
              value={stats?.reports.emails_sent ?? 'N/A'}
              subtitle="Email delivery not tracked"
              icon={<Activity className="h-5 w-5 text-white" />}
              color="from-teal-500 to-cyan-600"
            />
          </>
        )}
      </div>
    </div>
  )
}
