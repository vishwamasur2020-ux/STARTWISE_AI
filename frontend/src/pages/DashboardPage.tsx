/**
 * STARTWISE AI — Dashboard Page Component
 * Interactive dashboard home with Recharts metrics, quick actions, and recent predictions feed.
 */

import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  BrainCircuit,
  Store,
  TrendingUp,
  FileText,
  Plus,
  ArrowRight,
  ShieldCheck,
  Zap,
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts'

import { Button } from '@/components/ui/Button'
import { GlassCard, StatsCard } from '@/components/ui/Card'
import { useAuth } from '@/hooks/useAuth'

const TREND_DATA = [
  { month: 'Jan', probability: 72, roi: 24 },
  { month: 'Feb', probability: 78, roi: 28 },
  { month: 'Mar', probability: 85, roi: 32 },
  { month: 'Apr', probability: 82, roi: 30 },
  { month: 'May', probability: 91, roi: 38 },
  { month: 'Jun', probability: 94, roi: 42 },
]

const RECENT_PREDICTIONS = [
  {
    id: '1',
    name: 'Smart Chai Point Cafe',
    category: 'Food & Beverage',
    score: 92.4,
    risk: 'Low',
    roi: '45.0%',
    date: '2 hours ago',
  },
  {
    id: '2',
    name: 'Quick Parcel Logistics HUB',
    category: 'Retail & Logistics',
    score: 86.8,
    risk: 'Low',
    roi: '35.0%',
    date: 'Yesterday',
  },
  {
    id: '3',
    name: 'KidCare Premium Apparel',
    category: 'Retail',
    score: 78.2,
    risk: 'Medium',
    roi: '28.0%',
    date: '3 days ago',
  },
]

export default function DashboardPage() {
  const { user } = useAuth()
  const userName = user?.full_name?.split(' ')[0] || 'Founder'

  return (
    <div className="space-y-8 pb-12">
      {/* ── Welcome Banner ─────────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-indigo-500/10 backdrop-blur-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative overflow-hidden"
      >
        <div className="space-y-2 max-w-xl">
          <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            <Zap className="h-4 w-4" /> AI Advisor Active
          </div>
          <h1 className="text-2xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
            Welcome back, {userName} 👋
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-zinc-300 leading-relaxed">
            Ready to validate a new startup concept or explore high-ROI franchise opportunities today?
          </p>
        </div>

        <Link to="/startup-validation">
          <Button
            size="lg"
            leftIcon={<Plus className="h-5 w-5" />}
            className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-2xl shadow-lg shadow-cyan-500/20 whitespace-nowrap"
          >
            Validate New Idea
          </Button>
        </Link>
      </motion.div>

      {/* ── Stats Overview ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Ideas Validated"
          value="14"
          change="+3 this month"
          trend="up"
          icon={<BrainCircuit className="h-5 w-5" />}
        />
        <StatsCard
          title="Avg Success Score"
          value="88.4%"
          change="+4.2%"
          trend="up"
          icon={<ShieldCheck className="h-5 w-5 text-emerald-500" />}
        />
        <StatsCard
          title="Predicted ROI"
          value="36.5%"
          change="High Potential"
          trend="up"
          icon={<TrendingUp className="h-5 w-5 text-cyan-500" />}
        />
        <StatsCard
          title="Franchises Matched"
          value="28"
          change="Updated Today"
          trend="neutral"
          icon={<Store className="h-5 w-5 text-indigo-500" />}
        />
      </div>

      {/* ── Charts Grid ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Success Probability Trend */}
        <GlassCard className="p-6 sm:p-8 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Validation Success Trend</h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400">Historical AI prediction score trajectory</p>
            </div>
            <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-300">
              94.2% Accuracy
            </span>
          </div>

          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={TREND_DATA}>
                <defs>
                  <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" domain={[50, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderRadius: '12px',
                    borderColor: '#334155',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                />
                <Area type="monotone" dataKey="probability" stroke="#06B6D4" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Expected ROI Bar Chart */}
        <GlassCard className="p-6 sm:p-8 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">ROI Distribution</h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400">Projected annual payback percentage</p>
            </div>
            <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 bg-cyan-100 dark:bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-300">
              Avg 35% ROI
            </span>
          </div>

          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={TREND_DATA}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderRadius: '12px',
                    borderColor: '#334155',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="roi" fill="#4F46E5" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* ── Quick Actions & Recent Predictions ───────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Action Grid */}
        <GlassCard className="p-6 sm:p-8 space-y-4">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Quick Actions</h3>
          <div className="space-y-3">
            <Link
              to="/startup-validation"
              className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 hover:bg-cyan-50 dark:hover:bg-cyan-950/30 border border-slate-200/60 dark:border-zinc-700 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-xl bg-cyan-100 dark:bg-cyan-950/80 text-cyan-600 dark:text-cyan-400 flex items-center justify-center">
                  <BrainCircuit className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900 dark:text-white">AI Validation Wizard</p>
                  <p className="text-[10px] text-slate-500 dark:text-zinc-400">Validate a new business idea</p>
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-cyan-600 transition-colors" />
            </Link>

            <Link
              to="/franchise"
              className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 border border-slate-200/60 dark:border-zinc-700 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-xl bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                  <Store className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900 dark:text-white">Franchise Finder</p>
                  <p className="text-[10px] text-slate-500 dark:text-zinc-400">Match by capital budget</p>
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-indigo-600 transition-colors" />
            </Link>

            <Link
              to="/reports"
              className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 hover:bg-purple-50 dark:hover:bg-purple-950/30 border border-slate-200/60 dark:border-zinc-700 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-xl bg-purple-100 dark:bg-purple-950/80 text-purple-600 dark:text-purple-400 flex items-center justify-center">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900 dark:text-white">Executive PDF Reports</p>
                  <p className="text-[10px] text-slate-500 dark:text-zinc-400">Export investor decks</p>
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-purple-600 transition-colors" />
            </Link>
          </div>
        </GlassCard>

        {/* Recent Validations List */}
        <GlassCard className="lg:col-span-2 p-6 sm:p-8 space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Recent Analyses</h3>
            <Link to="/reports" className="text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline">
              View All Reports →
            </Link>
          </div>

          <div className="space-y-3">
            {RECENT_PREDICTIONS.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-4 rounded-2xl bg-slate-50/80 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-700/60 hover:border-cyan-500/40 transition-colors"
              >
                <div className="space-y-1">
                  <p className="text-sm font-bold text-slate-900 dark:text-white">{item.name}</p>
                  <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400">
                    <span>{item.category}</span>
                    <span>•</span>
                    <span>{item.date}</span>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-right">
                  <div>
                    <p className="text-sm font-black text-cyan-600 dark:text-cyan-400">{item.score}%</p>
                    <p className="text-[10px] text-slate-400">Success Rate</p>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase bg-emerald-100 text-emerald-700 border border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-300">
                    {item.risk} Risk
                  </span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
