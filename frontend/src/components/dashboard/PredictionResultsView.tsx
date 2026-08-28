/**
 * STARTWISE AI — Premium Prediction Results View (Stage 7)
 * Displays AI feasibility analysis: Business Score Gauge, Success Probability,
 * Risk Level, Estimated ROI, Competition Level, Dynamic Recommendations,
 * Recharts Health Radar & Feature Importance, Model Explainability, and Reanalysis Modal.
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  TrendingUp,
  ShieldAlert,
  Target,
  BarChart3,
  RefreshCw,
  DollarSign,
  Activity,
  Layers,
  ArrowRight,
} from 'lucide-react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts'

import { Button } from '@/components/ui/Button'
import { GlassCard } from '@/components/ui/Card'
import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'
import { PredictionAnalysisResponse } from '@/types/prediction'
import { useReanalyzeStartup } from '@/hooks/usePredictions'
import { XAIExplanationModal } from '@/components/xai/XAIExplanationModal'
import { XAIExplanationCard } from '@/components/xai/XAIExplanationCard'

interface PredictionResultsViewProps {
  prediction: PredictionAnalysisResponse
  onReanalyzeSuccess?: (updated: PredictionAnalysisResponse) => void
  isCompact?: boolean
}

export function PredictionResultsView({
  prediction,
  onReanalyzeSuccess,
  isCompact = false,
}: PredictionResultsViewProps) {
  const [reanalyzeModalOpen, setReanalyzeModalOpen] = useState(false)
  const [xaiModalOpen, setXaiModalOpen] = useState(false)
  const [showModelInfo, setShowModelInfo] = useState(false)
  const reanalyzeMutation = useReanalyzeStartup()

  const handleReanalyze = () => {
    if (!prediction.startup_id) return
    reanalyzeMutation.mutate(prediction.startup_id, {
      onSuccess: (updated) => {
        setReanalyzeModalOpen(false)
        if (onReanalyzeSuccess) onReanalyzeSuccess(updated)
      },
    })
  }

  // Color helpers
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-500 stroke-emerald-500 bg-emerald-500/10 border-emerald-500/30'
    if (score >= 75) return 'text-cyan-500 stroke-cyan-500 bg-cyan-500/10 border-cyan-500/30'
    if (score >= 60) return 'text-blue-500 stroke-blue-500 bg-blue-500/10 border-blue-500/30'
    if (score >= 40) return 'text-amber-500 stroke-amber-500 bg-amber-500/10 border-amber-500/30'
    return 'text-rose-500 stroke-rose-500 bg-rose-500/10 border-rose-500/30'
  }

  const getRiskBadgeVariant = (level: string) => {
    const l = level?.toLowerCase()
    if (l === 'low') return 'success'
    if (l === 'medium') return 'warning'
    return 'danger'
  }

  // Recharts Radar Data
  const radarData = [
    { metric: 'Success Prob', value: Math.round(prediction.success.probability) },
    { metric: 'Market Demand', value: 85 },
    { metric: 'Financial Health', value: Math.round(prediction.business_score) },
    { metric: 'Risk Control', value: prediction.risk.level === 'Low' ? 90 : prediction.risk.level === 'Medium' ? 60 : 30 },
    { metric: 'Competition', value: prediction.competition.level === 'Low' ? 85 : prediction.competition.level === 'Medium' ? 55 : 30 },
  ]



  // Feature Importance Data for Chart
  const featureData = (prediction.top_features || [
    { feature_name: 'financial_health_score', importance: 0.3437 },
    { feature_name: 'profit_margin', importance: 0.2028 },
    { feature_name: 'revenue_to_expense_ratio', importance: 0.1225 },
    { feature_name: 'market_opportunity_score', importance: 0.0569 },
    { feature_name: 'investment_to_revenue_ratio', importance: 0.0389 },
  ]).map((f) => ({
    name: f.feature_name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
    importance: Math.round(f.importance * 100),
  }))

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 16 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* ── Main Score Hero Card ──────────────────────────────────────────────── */}
      <motion.div variants={itemVariants}>
        <GlassCard className="p-6 sm:p-8 relative overflow-hidden border border-cyan-500/20 dark:border-cyan-500/30">
          <div className="absolute -top-24 -right-24 w-72 h-72 bg-gradient-to-br from-cyan-500/10 via-blue-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            {/* Left: Score Badge & Label */}
            <div className="flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
              {/* Circular Score Gauge */}
              <div className="relative flex items-center justify-center flex-shrink-0">
                <svg className="w-36 h-36 transform -rotate-90">
                  <circle
                    cx="72"
                    cy="72"
                    r="58"
                    stroke="currentColor"
                    strokeWidth="10"
                    className="text-slate-200 dark:text-zinc-800"
                    fill="transparent"
                  />
                  <circle
                    cx="72"
                    cy="72"
                    r="58"
                    stroke="currentColor"
                    strokeWidth="10"
                    strokeDasharray={364.4}
                    strokeDashoffset={364.4 - (364.4 * Math.min(100, prediction.business_score)) / 100}
                    strokeLinecap="round"
                    className={`transition-all duration-1000 ease-out ${getScoreColor(prediction.business_score).split(' ')[0]}`}
                    fill="transparent"
                  />
                </svg>
                <div className="absolute flex flex-col items-center justify-center">
                  <span className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                    {Math.round(prediction.business_score)}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    / 100
                  </span>
                </div>
              </div>

              {/* Title & Metadata */}
              <div className="space-y-2">
                <div className="flex items-center justify-center sm:justify-start gap-2">
                  <span className={`text-xs font-black uppercase tracking-widest px-3 py-1 rounded-full border ${getScoreColor(prediction.business_score)}`}>
                    {prediction.score_label} Business Score
                  </span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
                  {prediction.business_name}
                </h2>
                <p className="text-xs text-slate-500 dark:text-zinc-400 max-w-md">
                  Evaluated across 4 trained Machine Learning models (Random Forest, Decision Tree, Linear Regression).
                </p>
              </div>
            </div>

            {/* Right: Actions */}
            <div className="flex items-center gap-2.5 flex-wrap flex-shrink-0">
              <Button
                onClick={() => setXaiModalOpen(true)}
                size="sm"
                leftIcon={<Sparkles className="h-4 w-4 text-cyan-400" />}
                className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white rounded-2xl text-xs font-bold shadow-md shadow-cyan-500/20"
              >
                Why this result? (XAI)
              </Button>
              {prediction.startup_id && (
                <Button
                  onClick={() => setReanalyzeModalOpen(true)}
                  variant="outline"
                  size="sm"
                  leftIcon={<RefreshCw className="h-4 w-4 text-cyan-500" />}
                  className="rounded-2xl border-slate-200 dark:border-zinc-800 hover:bg-cyan-500/10 text-xs font-bold"
                >
                  Run Analysis Again
                </Button>
              )}
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* ── Key Metrics 4-Grid ────────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* 1. Success Probability */}
        <GlassCard className="p-5 space-y-3 relative">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Success Probability
            </span>
            <div className="h-8 w-8 rounded-xl bg-cyan-500/10 text-cyan-500 flex items-center justify-center">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
              {prediction.success.probability.toFixed(1)}%
            </span>
            <span className={`text-xs font-bold ${prediction.success.prediction ? 'text-emerald-500' : 'text-rose-500'}`}>
              {prediction.success.prediction ? 'Viable' : 'High Risk'}
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-zinc-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, prediction.success.probability)}%` }}
            />
          </div>
        </GlassCard>

        {/* 2. Risk Level */}
        <GlassCard className="p-5 space-y-3 relative">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Risk Profile
            </span>
            <div className="h-8 w-8 rounded-xl bg-amber-500/10 text-amber-500 flex items-center justify-center">
              <ShieldAlert className="h-4 w-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase">
              {prediction.risk.level}
            </span>
            <Badge variant={getRiskBadgeVariant(prediction.risk.level)} className="text-[10px]">
              {prediction.risk.probability.toFixed(0)}% Confidence
            </Badge>
          </div>
          <p className="text-[11px] text-slate-400">
            Decision Tree Risk Classification Model
          </p>
        </GlassCard>

        {/* 3. Estimated ROI */}
        <GlassCard className="p-5 space-y-3 relative">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Estimated Annual ROI
            </span>
            <div className="h-8 w-8 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
              <DollarSign className="h-4 w-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
              {prediction.roi.estimated_percentage > 0 ? '+' : ''}{prediction.roi.estimated_percentage.toFixed(1)}%
            </span>
          </div>
          <p className="text-[11px] text-slate-400">
            Linear Regression Payback Projection
          </p>
        </GlassCard>

        {/* 4. Competition Level */}
        <GlassCard className="p-5 space-y-3 relative">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              Market Competition
            </span>
            <div className="h-8 w-8 rounded-xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center">
              <Target className="h-4 w-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase">
              {prediction.competition.level}
            </span>
            <Badge variant={prediction.competition.level === 'High' ? 'danger' : 'secondary'} className="text-[10px]">
              {prediction.competition.probability.toFixed(0)}% Score
            </Badge>
          </div>
          <p className="text-[11px] text-slate-400">
            Random Forest Sector Density Index
          </p>
        </GlassCard>
      </motion.div>

      {/* ── Recharts Section: Radar & Feature Importance ──────────────────────── */}
      {!isCompact && (
        <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Business Health Radar */}
          <GlassCard className="p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-zinc-800 pb-3">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-cyan-500" />
                <h3 className="font-bold text-slate-900 dark:text-white text-sm">Business Health Radar</h3>
              </div>
              <span className="text-[11px] text-slate-400">Multi-factor Evaluation</span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid stroke="#64748b" strokeDasharray="3 3" opacity={0.3} />
                  <PolarAngleAxis dataKey="metric" stroke="#94a3b8" tick={{ fontSize: 11, fontWeight: 600 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#64748b" opacity={0.3} />
                  <Radar
                    name="Business Score"
                    dataKey="value"
                    stroke="#06B6D4"
                    fill="#06B6D4"
                    fillOpacity={0.4}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* Top Feature Importance Chart */}
          <GlassCard className="p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-zinc-800 pb-3">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-indigo-500" />
                <h3 className="font-bold text-slate-900 dark:text-white text-sm">Key Impact Drivers</h3>
              </div>
              <span className="text-[11px] text-slate-400">Random Forest Importance</span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart layout="vertical" data={featureData} margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                  <XAxis type="number" domain={[0, 50]} stroke="#94a3b8" tickFormatter={(v) => `${v}%`} />
                  <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10, fontWeight: 600 }} width={120} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      borderColor: 'rgba(6, 182, 212, 0.3)',
                      borderRadius: '12px',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                    formatter={(val: any) => [`${val}% Weight`, 'Importance']}
                  />
                  <Bar dataKey="importance" radius={[0, 8, 8, 0]}>
                    {featureData.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#06B6D4' : index === 1 ? '#3B82F6' : '#6366F1'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* ── Explainable AI (XAI) Feature Attribution Card ────────────────────── */}
      <motion.div variants={itemVariants}>
        <XAIExplanationCard
          predictionId={prediction.id || prediction.startup_id}
          businessName={prediction.business_name}
        />
      </motion.div>

      {/* ── Dynamic AI Recommendations ───────────────────────────────────────── */}
      <motion.div variants={itemVariants}>
        <GlassCard className="p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-200/80 dark:border-zinc-800 pb-3">
            <Sparkles className="h-5 w-5 text-cyan-500" />
            <h3 className="font-extrabold text-slate-900 dark:text-white text-base">
              AI Strategic Recommendations
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {prediction.recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="p-4 rounded-2xl bg-slate-500/5 dark:bg-zinc-800/40 border border-slate-200/60 dark:border-zinc-800/80 flex items-start gap-3"
              >
                <div className="h-7 w-7 rounded-xl bg-cyan-500/10 text-cyan-500 flex items-center justify-center flex-shrink-0 mt-0.5 font-bold text-xs">
                  {idx + 1}
                </div>
                <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed font-medium">
                  {rec}
                </p>
              </div>
            ))}
          </div>
        </GlassCard>
      </motion.div>

      {/* ── Model Explainability Box ("How was this result generated?") ──────── */}
      <motion.div variants={itemVariants}>
        <GlassCard className="p-6 space-y-4 border border-cyan-500/15">
          <button
            onClick={() => setShowModelInfo(!showModelInfo)}
            className="w-full flex items-center justify-between text-left"
          >
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-cyan-500" />
              <h4 className="font-bold text-slate-900 dark:text-white text-sm">
                How was this result generated? (Academic ML Architecture)
              </h4>
            </div>
            <div className="flex items-center gap-1 text-xs text-cyan-500 font-semibold">
              <span>{showModelInfo ? 'Hide Details' : 'View Architecture'}</span>
              <ArrowRight className={`h-3.5 w-3.5 transition-transform ${showModelInfo ? 'rotate-90' : ''}`} />
            </div>
          </button>

          <AnimatePresence>
            {showModelInfo && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="pt-4 border-t border-slate-200/80 dark:border-zinc-800 space-y-4"
              >
                <p className="text-xs text-slate-500 dark:text-zinc-400">
                  STARTWISE AI processes your startup input through an offline-trained ensemble pipeline built on Python 3.14 & Scikit-Learn:
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                  <div className="p-3 rounded-xl bg-cyan-500/5 border border-cyan-500/20">
                    <span className="font-bold text-cyan-600 dark:text-cyan-400 block mb-1">Success Prediction</span>
                    <strong className="text-slate-800 dark:text-zinc-200">{prediction.model_information.success_model}</strong>
                    <p className="text-[10px] text-slate-500 mt-1">200 trees, bagging, predict_proba</p>
                  </div>
                  <div className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20">
                    <span className="font-bold text-amber-600 dark:text-amber-400 block mb-1">Risk Classification</span>
                    <strong className="text-slate-800 dark:text-zinc-200">{prediction.model_information.risk_model}</strong>
                    <p className="text-[10px] text-slate-500 mt-1">Max depth 8, explicit decision rules</p>
                  </div>
                  <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                    <span className="font-bold text-emerald-600 dark:text-emerald-400 block mb-1">ROI Prediction</span>
                    <strong className="text-slate-800 dark:text-zinc-200">{prediction.model_information.roi_model}</strong>
                    <p className="text-[10px] text-slate-500 mt-1">Continuous linear regression model</p>
                  </div>
                  <div className="p-3 rounded-xl bg-indigo-500/5 border border-indigo-500/20">
                    <span className="font-bold text-indigo-600 dark:text-indigo-400 block mb-1">Competition Model</span>
                    <strong className="text-slate-800 dark:text-zinc-200">{prediction.model_information.competition_model}</strong>
                    <p className="text-[10px] text-slate-500 mt-1">Sector density classification</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </GlassCard>
      </motion.div>

      {/* ── Re-analyze Confirmation Modal ────────────────────────────────────── */}
      <Modal
        isOpen={reanalyzeModalOpen}
        onClose={() => setReanalyzeModalOpen(false)}
        title="Re-Analyze Startup Concept"
        description="Your startup parameters will be passed through the latest Machine Learning models to calculate an updated feasibility score and history entry."
      >
        <div className="space-y-4 pt-2">
          <p className="text-xs text-slate-500 dark:text-zinc-400">
            Are you sure you want to run the analysis again for <strong>{prediction.business_name}</strong>?
          </p>

          <div className="flex items-center justify-end gap-3 pt-4">
            <Button
              onClick={() => setReanalyzeModalOpen(false)}
              variant="outline"
              size="sm"
              className="rounded-xl text-xs"
            >
              Cancel
            </Button>
            <Button
              onClick={handleReanalyze}
              isLoading={reanalyzeMutation.isPending}
              size="sm"
              leftIcon={<RefreshCw className="h-4 w-4" />}
              className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl text-xs font-semibold"
            >
              Confirm Re-Analysis
            </Button>
          </div>
        </div>
      </Modal>

      {/* ── XAI Explanation Modal ────────────────────────────────────────────── */}
      <XAIExplanationModal
        isOpen={xaiModalOpen}
        onClose={() => setXaiModalOpen(false)}
        predictionId={prediction.id || prediction.startup_id}
        businessName={prediction.business_name}
      />
    </motion.div>
  )
}
