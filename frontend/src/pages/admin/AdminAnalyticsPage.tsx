/**
 * STARTWISE AI — Admin Analytics Page (Stage 12)
 * Real time-series data from PostgreSQL via admin analytics endpoint.
 */

import { useState } from 'react'
import { RefreshCw } from 'lucide-react'
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area,
  BarChart, Bar, PieChart, Pie, Cell, Legend,
  XAxis, YAxis, Tooltip, CartesianGrid,
} from 'recharts'
import { useAdminAnalytics } from '@/hooks/useAdmin'

const PIE_COLORS = ['#10b981', '#f59e0b', '#ef4444', '#6366f1', '#06b6d4', '#f43f5e', '#a78bfa']

const TOOLTIP_STYLE = {
  contentStyle: { background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 },
  labelStyle: { color: '#fff', fontWeight: 700 },
  itemStyle: { color: '#94a3b8' },
}

interface ChartCardProps {
  title: string
  children: React.ReactNode
  loading: boolean
}

function ChartCard({ title, children, loading }: ChartCardProps) {
  return (
    <div className="bg-slate-900 border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-bold text-white mb-4">{title}</h3>
      {loading ? (
        <div className="h-48 bg-slate-800 rounded-xl animate-pulse" />
      ) : children}
    </div>
  )
}

function EmptyChart() {
  return <div className="h-48 flex items-center justify-center text-slate-600 text-sm">No data available yet.</div>
}

export default function AdminAnalyticsPage() {
  const [groupBy, setGroupBy] = useState<'day' | 'month'>('month')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const params = { group_by: groupBy, start_date: startDate || undefined, end_date: endDate || undefined }
  const { data, isLoading, refetch, isFetching } = useAdminAnalytics(params)
  const analytics = data as any

  function formatDate(d: string) {
    if (!d) return ''
    if (groupBy === 'month') {
      const [year, month] = d.split('-')
      return new Date(Number(year), Number(month) - 1).toLocaleString('en-IN', { month: 'short', year: '2-digit' })
    }
    return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
  }

  const userGrowth = (analytics?.user_growth ?? []).map((p: any) => ({ ...p, date: formatDate(p.date) }))
  const startupCreation = (analytics?.startup_creation ?? []).map((p: any) => ({ ...p, date: formatDate(p.date) }))
  const analysisVolume = (analytics?.analysis_volume ?? []).map((p: any) => ({ ...p, date: formatDate(p.date) }))
  const riskDist = analytics?.risk_distribution ?? []
  const catDist = (analytics?.category_distribution ?? []).slice(0, 8)
  const reportGen = (analytics?.report_generation ?? []).map((p: any) => ({ ...p, date: formatDate(p.date) }))
  const scoreTrend = (analytics?.avg_business_score_trend ?? []).map((p: any) => ({ ...p, date: formatDate(p.date) }))

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-black text-white">Platform Analytics</h1>
          <p className="text-sm text-slate-400 mt-1">Real database time-series analytics</p>
        </div>
        <button onClick={() => refetch()} disabled={isFetching} className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-white/10 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-700 transition-colors">
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-1 bg-slate-800 border border-white/10 rounded-xl p-1">
          {(['day', 'month'] as const).map(g => (
            <button
              key={g}
              onClick={() => setGroupBy(g)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${groupBy === g ? 'bg-amber-500 text-slate-900' : 'text-slate-400 hover:text-white'}`}
            >
              By {g.charAt(0).toUpperCase() + g.slice(1)}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="px-3 py-2 bg-slate-800 border border-white/10 rounded-xl text-xs text-slate-300 focus:outline-none" />
          <span className="text-slate-600 text-xs">to</span>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="px-3 py-2 bg-slate-800 border border-white/10 rounded-xl text-xs text-slate-300 focus:outline-none" />
        </div>
        {(startDate || endDate) && (
          <button onClick={() => { setStartDate(''); setEndDate('') }} className="text-xs text-slate-400 hover:text-white transition-colors">Clear dates</button>
        )}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Growth */}
        <ChartCard title="User Growth" loading={isLoading}>
          {userGrowth.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={userGrowth}>
                <defs>
                  <linearGradient id="userGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Area type="monotone" dataKey="value" stroke="#06b6d4" strokeWidth={2} fill="url(#userGrad)" name="New Users" />
              </AreaChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </ChartCard>

        {/* Startup Creation */}
        <ChartCard title="Startup Submissions" loading={isLoading}>
          {startupCreation.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={startupCreation}>
                <defs>
                  <linearGradient id="startupGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Area type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={2} fill="url(#startupGrad)" name="Startups" />
              </AreaChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </ChartCard>

        {/* Analysis Volume */}
        <ChartCard title="AI Analysis Volume" loading={isLoading}>
          {analysisVolume.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={analysisVolume} barSize={20}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} name="Analyses" />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </ChartCard>

        {/* Risk Distribution */}
        <ChartCard title="Risk Distribution" loading={isLoading}>
          {riskDist.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={riskDist.map((d: any) => ({ name: d.label, value: d.count }))} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={3} dataKey="value">
                  {riskDist.map((_: any, i: number) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{v}</span>} />
                <Tooltip {...TOOLTIP_STYLE} />
              </PieChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </ChartCard>

        {/* Category Distribution */}
        <ChartCard title="Startup Categories" loading={isLoading}>
          {catDist.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={catDist.map((d: any) => ({ name: d.label, value: d.count }))} barSize={20} layout="vertical">
                <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis dataKey="name" type="category" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} width={80} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Bar dataKey="value" fill="#f59e0b" radius={[0, 4, 4, 0]} name="Startups" />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </ChartCard>

        {/* Avg Business Score Trend */}
        <ChartCard title="Avg Business Score Trend" loading={isLoading}>
          {scoreTrend.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={scoreTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 100]} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Line type="monotone" dataKey="value" stroke="#a78bfa" strokeWidth={2} dot={{ fill: '#a78bfa', r: 3 }} name="Avg Score" />
              </LineChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </ChartCard>

        {/* Report Generation */}
        <ChartCard title="Report Generation" loading={isLoading}>
          {reportGen.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={reportGen} barSize={20}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Bar dataKey="value" fill="#f43f5e" radius={[4, 4, 0, 0]} name="Reports" />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </ChartCard>
      </div>
    </div>
  )
}
