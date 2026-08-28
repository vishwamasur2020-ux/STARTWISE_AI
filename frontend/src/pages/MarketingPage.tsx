/**
 * STARTWISE AI — AI Marketing Strategy Dashboard Page (Stage 9)
 * Comprehensive, multi-channel marketing intelligence hub featuring:
 *   - Overall Strategy Score Gauge (0-100) & Strategy Type Selector
 *   - Top Scored Marketing Channels with dynamic explanations
 *   - Recharts Donut Chart for Budget Allocation
 *   - 30-Day Marketing Plan Timeline (Week 1-4)
 *   - Personalized Campaign Ideas Cards
 *   - Content Strategy Tabs (Social, Video, Blog, Email, WhatsApp)
 *   - Relevant Channel KPIs Dashboard
 *   - Strategy Regeneration Modal
 */

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import {
  Megaphone,
  Sparkles,
  TrendingUp,
  DollarSign,
  Calendar,
  CheckCircle2,
  Share2,
  Video,
  Mail,
  MessageSquare,
  Layers,
  RefreshCw,
  Info,
  Building2,
} from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { GlassCard } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Modal } from '@/components/ui/Modal'

import { useStartups } from '@/hooks/useStartups'
import { useMarketingStrategy, useRegenerateMarketing, useAnalyzeMarketing } from '@/hooks/useMarketing'

const COLORS = ['#06b6d4', '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899', '#6366f1']

export default function MarketingPage() {
  const { id: routeStartupId } = useParams<{ id?: string }>()
  const navigate = useNavigate()

  const { data: startups = [], isLoading: startupsLoading } = useStartups()
  const [selectedStartupId, setSelectedStartupId] = useState<string>(routeStartupId || '')

  // Fallback to first available startup if none selected
  const activeStartupId = selectedStartupId || (startups.length > 0 ? startups[0].id : '')
  const activeStartup = startups.find((s: any) => s.id === activeStartupId)

  // Marketing Query & Mutations
  const { data: strategy, isLoading: strategyLoading, error: strategyError } = useMarketingStrategy(
    activeStartupId,
    !!activeStartupId
  )
  const analyzeMutation = useAnalyzeMarketing()
  const regenerateMutation = useRegenerateMarketing()

  // UI Local States
  const [activeStrategyType, setActiveStrategyType] = useState<'LOW_BUDGET' | 'BALANCED' | 'AGGRESSIVE'>('BALANCED')
  const [activeContentTab, setActiveContentTab] = useState<'social' | 'video' | 'blog' | 'email' | 'whatsapp'>('social')
  const [confirmRegenOpen, setConfirmRegenOpen] = useState(false)

  // Run initial analysis
  const handleRunAnalysis = () => {
    if (!activeStartupId) {
      toast.error('Please select a valid startup idea.')
      return
    }
    analyzeMutation.mutate(activeStartupId)
  }

  // Handle strategy regeneration
  const handleRegenerate = () => {
    if (!activeStartupId) return
    regenerateMutation.mutate(activeStartupId, {
      onSuccess: () => {
        setConfirmRegenOpen(false)
      },
    })
  }

  // Build Pie Chart Data for Budget Allocation
  const activeScenario = strategy?.budget_allocation?.scenarios?.[activeStrategyType]
  const pieData = activeScenario
    ? Object.entries(activeScenario.allocation).map(([name, value]) => ({
        name,
        value: Number(value),
      }))
    : []

  return (
    <div className="space-y-8 pb-16">
      <Breadcrumb items={[{ label: 'AI Marketing Strategy' }]} />

      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            <Megaphone className="h-4 w-4" /> AI Marketing & Promotion Engine
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
            Personalized Marketing Strategy
          </h1>
          <p className="text-sm text-slate-500 dark:text-zinc-400 max-w-2xl">
            Multi-channel recommendations, budget allocation, 30-day timeline tasks, and relevant KPIs tailored to your startup ML results.
          </p>
        </div>

        {/* Startup Selector Dropdown */}
        {startups.length > 1 && (
          <div className="flex items-center gap-3 bg-slate-500/5 p-2 rounded-2xl border border-slate-200/80 dark:border-zinc-800">
            <Building2 className="h-4 w-4 text-cyan-500 ml-2" />
            <select
              value={activeStartupId}
              onChange={(e) => {
                setSelectedStartupId(e.target.value)
                navigate(`/startup-validation/${e.target.value}/marketing`)
              }}
              className="bg-transparent text-xs font-bold text-slate-900 dark:text-white outline-none cursor-pointer pr-4"
            >
              {startups.map((s: any) => (
                <option key={s.id} value={s.id} className="dark:bg-zinc-900">
                  {s.business_name} ({s.business_category})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* ── Main Strategy Dashboard Content ─────────────────────────────────── */}
      <AnimatePresence mode="wait">
        {strategyLoading || startupsLoading ? (
          <GlassCard className="p-12 text-center space-y-4">
            <div className="relative w-16 h-16 mx-auto flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-4 border-cyan-500/20 border-t-cyan-500 animate-spin" />
              <Megaphone className="h-8 w-8 text-cyan-500 animate-pulse" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              AI is building your personalized marketing strategy...
            </h3>
            <p className="text-xs text-slate-500">
              Scoring 19 marketing channels, allocating budget scenarios, and generating 30-day timeline tasks...
            </p>
          </GlassCard>
        ) : strategyError || !strategy ? (
          /* Empty / Missing Prediction State */
          <GlassCard className="p-8 text-center space-y-6 max-w-xl mx-auto border-amber-500/30">
            <div className="h-16 w-16 rounded-full bg-amber-500/10 text-amber-500 flex items-center justify-center mx-auto">
              <Info className="h-8 w-8" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-black text-slate-900 dark:text-white">
                Startup Analysis Prerequisite Required
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400">
                Complete your AI startup feasibility analysis before generating a personalized marketing strategy.
              </p>
            </div>
            <div className="flex items-center justify-center gap-4">
              <Button
                onClick={() => navigate(`/startup-validation`)}
                size="sm"
                className="bg-cyan-500 text-white font-bold rounded-xl"
              >
                Run Startup Analysis
              </Button>
              {activeStartupId && (
                <Button
                  onClick={handleRunAnalysis}
                  isLoading={analyzeMutation.isPending}
                  size="sm"
                  variant="secondary"
                  className="rounded-xl font-bold"
                >
                  Generate Strategy Now
                </Button>
              )}
            </div>
          </GlassCard>
        ) : (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
            {/* ── 1. Strategy Overview Header Card ───────────────────────────── */}
            <GlassCard className="p-6 sm:p-8 relative overflow-hidden border border-cyan-500/30 bg-gradient-to-br from-cyan-500/5 via-blue-500/5 to-transparent">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
                {/* Score Gauge & Overview */}
                <div className="flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
                  <div className="h-28 w-28 rounded-3xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white font-black text-3xl flex flex-col items-center justify-center shadow-xl shadow-cyan-500/30 flex-shrink-0">
                    <span>{Math.round(strategy.marketing_score)}</span>
                    <span className="text-[10px] font-bold tracking-widest uppercase opacity-80">/ 100</span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-center sm:justify-start gap-2">
                      <Badge variant="primary">{strategy.strategy_label}</Badge>
                      <Badge variant="secondary">{strategy.profile?.category || 'Omnichannel'}</Badge>
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
                      {activeStartup?.business_name || 'Your Startup'} Marketing Plan
                    </h2>
                    <p className="text-xs text-slate-500 dark:text-zinc-400">
                      Recommended Initial Marketing Budget:{' '}
                      <strong className="text-emerald-600 dark:text-emerald-400 font-extrabold text-sm">
                        ₹{(strategy.total_recommended_budget / 1000).toFixed(0)}k INR
                      </strong>
                    </p>
                  </div>
                </div>

                {/* Controls & Strategy Type Selector */}
                <div className="flex flex-col items-end gap-3 w-full lg:w-auto">
                  <Button
                    onClick={() => setConfirmRegenOpen(true)}
                    size="sm"
                    variant="secondary"
                    leftIcon={<RefreshCw className="h-4 w-4 text-cyan-500" />}
                    className="rounded-xl font-bold text-xs"
                  >
                    Regenerate Strategy
                  </Button>

                  {/* Scenario Toggle */}
                  <div className="flex items-center gap-1 bg-slate-500/10 p-1 rounded-xl border border-slate-200/80 dark:border-zinc-800 text-[11px] font-bold">
                    <button
                      onClick={() => setActiveStrategyType('LOW_BUDGET')}
                      className={`px-3 py-1.5 rounded-lg transition-all ${
                        activeStrategyType === 'LOW_BUDGET'
                          ? 'bg-cyan-500 text-white shadow-md'
                          : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      Low Budget
                    </button>
                    <button
                      onClick={() => setActiveStrategyType('BALANCED')}
                      className={`px-3 py-1.5 rounded-lg transition-all ${
                        activeStrategyType === 'BALANCED'
                          ? 'bg-cyan-500 text-white shadow-md'
                          : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      Balanced
                    </button>
                    <button
                      onClick={() => setActiveStrategyType('AGGRESSIVE')}
                      className={`px-3 py-1.5 rounded-lg transition-all ${
                        activeStrategyType === 'AGGRESSIVE'
                          ? 'bg-cyan-500 text-white shadow-md'
                          : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      Aggressive
                    </button>
                  </div>
                </div>
              </div>
            </GlassCard>

            {/* ── 2. Top Scored Recommended Channels & Budget Donut Chart ────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Top Channels Cards (Col 2) */}
              <div className="lg:col-span-2 space-y-4">
                <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-cyan-500" /> Top Scored Marketing Channels
                </h3>

                <div className="space-y-4">
                  {strategy.recommended_channels.map((ch) => (
                    <GlassCard key={ch.channel_name} className="p-5 space-y-3 border hover:border-cyan-500/40 transition-all">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center gap-3">
                          <span className="h-8 w-8 rounded-xl bg-cyan-500/10 text-cyan-500 font-black text-xs flex items-center justify-center">
                            #{ch.ranking_position}
                          </span>
                          <div>
                            <h4 className="text-base font-extrabold text-slate-900 dark:text-white">
                              {ch.channel_name}
                            </h4>
                            <span className="text-[11px] text-slate-400 font-medium">{ch.platform}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-3">
                          <Badge variant={ch.marketing_score >= 85 ? 'success' : 'primary'}>
                            {ch.marketing_score}% Fit Score
                          </Badge>
                          <strong className="text-xs font-black text-emerald-600 dark:text-emerald-400">
                            ₹{ch.allocated_budget.toLocaleString()} INR
                          </strong>
                        </div>
                      </div>

                      {/* Explanation Reasons */}
                      <div className="space-y-1 text-xs pt-2 border-t border-slate-200/80 dark:border-zinc-800">
                        {ch.explanation.map((exp, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-slate-600 dark:text-zinc-300">
                            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                            <span>{exp}</span>
                          </div>
                        ))}
                      </div>
                    </GlassCard>
                  ))}
                </div>
              </div>

              {/* Budget Allocation Donut Chart (Col 1) */}
              <GlassCard className="p-6 space-y-4 flex flex-col justify-between">
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-emerald-500" /> Budget Allocation Breakdown
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    {activeScenario?.description || 'Allocated marketing budget per channel'}
                  </p>
                </div>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={80}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {pieData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: any) => `₹${Number(value || 0).toLocaleString()} INR`} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Legend list */}
                <div className="space-y-1 text-xs pt-2 border-t border-slate-200/80 dark:border-zinc-800 max-h-40 overflow-y-auto">
                  {pieData.map((item, idx) => (
                    <div key={item.name} className="flex items-center justify-between text-slate-600 dark:text-zinc-300">
                      <div className="flex items-center gap-2">
                        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                        <span className="truncate max-w-[140px]">{item.name}</span>
                      </div>
                      <strong className="font-bold">₹{item.value.toLocaleString()}</strong>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </div>

            {/* ── 3. Personalized Campaign Ideas ─────────────────────────────────── */}
            <div className="space-y-4">
              <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                <Megaphone className="h-5 w-5 text-indigo-500" /> High-Impact Campaign Concepts
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {strategy.campaign_ideas.map((camp, idx) => (
                  <GlassCard key={idx} className="p-6 space-y-3 border hover:border-indigo-500/40 transition-all flex flex-col justify-between">
                    <div className="space-y-2">
                      <Badge variant="primary" className="text-[10px]">
                        {camp.platform}
                      </Badge>
                      <h4 className="text-base font-extrabold text-slate-900 dark:text-white">
                        {camp.campaign_name}
                      </h4>
                      <p className="text-xs text-slate-500 dark:text-zinc-400">
                        {camp.description}
                      </p>
                    </div>

                    <div className="space-y-2 pt-3 border-t border-slate-200/80 dark:border-zinc-800 text-xs">
                      <div className="flex justify-between text-slate-600 dark:text-zinc-300">
                        <span className="text-slate-400">Est. Budget:</span>
                        <strong className="font-bold text-emerald-600 dark:text-emerald-400">
                          ₹{camp.estimated_budget.toLocaleString()} INR
                        </strong>
                      </div>
                      <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 font-bold text-[11px] text-center">
                        CTA: {camp.call_to_action}
                      </div>
                    </div>
                  </GlassCard>
                ))}
              </div>
            </div>

            {/* ── 4. 30-Day Marketing Plan Timeline ──────────────────────────────── */}
            <div className="space-y-4">
              <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                <Calendar className="h-5 w-5 text-cyan-500" /> 30-Day Marketing Execution Plan
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {strategy.thirty_day_plan.map((phase) => (
                  <GlassCard key={phase.week} className="p-5 space-y-4 border border-cyan-500/20">
                    <div className="flex items-center gap-3">
                      <span className="h-10 w-10 rounded-2xl bg-cyan-500 text-white font-black text-sm flex items-center justify-center shadow-md">
                        W{phase.week}
                      </span>
                      <div>
                        <h4 className="text-xs font-black uppercase text-cyan-600 dark:text-cyan-400 tracking-wider">
                          Week {phase.week} Phase
                        </h4>
                        <p className="text-xs font-bold text-slate-900 dark:text-white">{phase.phase}</p>
                      </div>
                    </div>

                    <div className="space-y-3 pt-2">
                      {phase.tasks.map((task, tIdx) => (
                        <div key={tIdx} className="p-3 rounded-xl bg-slate-500/5 dark:bg-zinc-800/40 border border-slate-200/80 dark:border-zinc-800 space-y-1 text-xs">
                          <strong className="font-bold text-slate-900 dark:text-white block">
                            {task.task_name}
                          </strong>
                          <span className="text-[10px] text-cyan-600 dark:text-cyan-400 font-medium block">
                            Channel: {task.channel}
                          </span>
                          <span className="text-[11px] text-slate-500 block">
                            KPI: {task.kpis}
                          </span>
                        </div>
                      ))}
                    </div>
                  </GlassCard>
                ))}
              </div>
            </div>

            {/* ── 5. Content Strategy Tabs ───────────────────────────────────────── */}
            <GlassCard className="p-6 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/80 dark:border-zinc-800 pb-4">
                <div className="space-y-1">
                  <h3 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                    <Layers className="h-5 w-5 text-purple-500" /> Content Strategy & Copy Templates
                  </h3>
                  <p className="text-xs text-slate-500">Ready-to-use content ideas across platforms</p>
                </div>

                {/* Tabs */}
                <div className="flex items-center gap-1 bg-slate-500/10 p-1 rounded-xl text-xs font-bold">
                  <button
                    onClick={() => setActiveContentTab('social')}
                    className={`px-3 py-1.5 rounded-lg transition-all ${
                      activeContentTab === 'social' ? 'bg-cyan-500 text-white' : 'text-slate-500'
                    }`}
                  >
                    Social Posts
                  </button>
                  <button
                    onClick={() => setActiveContentTab('video')}
                    className={`px-3 py-1.5 rounded-lg transition-all ${
                      activeContentTab === 'video' ? 'bg-cyan-500 text-white' : 'text-slate-500'
                    }`}
                  >
                    Reels/Shorts
                  </button>
                  <button
                    onClick={() => setActiveContentTab('email')}
                    className={`px-3 py-1.5 rounded-lg transition-all ${
                      activeContentTab === 'email' ? 'bg-cyan-500 text-white' : 'text-slate-500'
                    }`}
                  >
                    Email Copy
                  </button>
                  <button
                    onClick={() => setActiveContentTab('whatsapp')}
                    className={`px-3 py-1.5 rounded-lg transition-all ${
                      activeContentTab === 'whatsapp' ? 'bg-cyan-500 text-white' : 'text-slate-500'
                    }`}
                  >
                    WhatsApp Broadcast
                  </button>
                </div>
              </div>

              {/* Tab Content Display */}
              <div className="space-y-3 text-xs">
                {activeContentTab === 'social' && (
                  <div className="space-y-2">
                    {(strategy.content_strategy?.social_media_posts || []).map((post, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-slate-500/5 dark:bg-zinc-800/40 border border-slate-200/80 dark:border-zinc-800 flex items-start gap-2">
                        <Share2 className="h-4 w-4 text-cyan-500 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-700 dark:text-zinc-300">{post}</span>
                      </div>
                    ))}
                  </div>
                )}

                {activeContentTab === 'video' && (
                  <div className="space-y-2">
                    {(strategy.content_strategy?.reels_and_shorts || []).map((vid, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-slate-500/5 dark:bg-zinc-800/40 border border-slate-200/80 dark:border-zinc-800 flex items-start gap-2">
                        <Video className="h-4 w-4 text-purple-500 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-700 dark:text-zinc-300">{vid}</span>
                      </div>
                    ))}
                  </div>
                )}

                {activeContentTab === 'email' && (
                  <div className="space-y-2">
                    {(strategy.content_strategy?.email_templates || []).map((em, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-slate-500/5 dark:bg-zinc-800/40 border border-slate-200/80 dark:border-zinc-800 flex items-start gap-2">
                        <Mail className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-700 dark:text-zinc-300">{em}</span>
                      </div>
                    ))}
                  </div>
                )}

                {activeContentTab === 'whatsapp' && (
                  <div className="space-y-2">
                    {(strategy.content_strategy?.whatsapp_messages || []).map((msg, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-start gap-2">
                        <MessageSquare className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-700 dark:text-zinc-300">{msg}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </GlassCard>

            {/* ── 6. Relevant KPIs Dashboard ────────────────────────────────────── */}
            <div className="space-y-4">
              <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-emerald-500" /> Target KPIs & Performance Benchmarks
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                {strategy.kpis.map((kpi, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-500/5 dark:bg-zinc-800/40 border border-slate-200/80 dark:border-zinc-800 space-y-1">
                    <span className="text-[10px] text-slate-400 block font-semibold uppercase tracking-wider">
                      {kpi.category}
                    </span>
                    <strong className="text-sm font-black text-slate-900 dark:text-white block">
                      {kpi.metric}
                    </strong>
                    <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 block">
                      {kpi.target}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Disclaimer */}
            <div className="flex items-start gap-2 text-[10px] text-slate-400 bg-slate-500/5 p-4 rounded-2xl">
              <Info className="h-4 w-4 text-cyan-500 flex-shrink-0 mt-0.5" />
              <span>{strategy.disclaimer}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Confirm Regeneration Modal ─────────────────────────────────────── */}
      <Modal
        isOpen={confirmRegenOpen}
        onClose={() => setConfirmRegenOpen(false)}
        title="Regenerate Marketing Strategy"
        description="Are you sure you want to recalculate and generate a new AI marketing strategy for this startup idea?"
      >
        <div className="space-y-6 pt-2">
          <p className="text-xs text-slate-500">
            This will evaluate current ML outputs, re-score marketing channels, and save a new strategy entry in your account history.
          </p>

          <div className="flex items-center justify-end gap-3">
            <Button size="sm" variant="secondary" onClick={() => setConfirmRegenOpen(false)}>
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleRegenerate}
              isLoading={regenerateMutation.isPending}
              className="bg-cyan-500 text-white font-bold rounded-xl"
            >
              Confirm Regeneration
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
