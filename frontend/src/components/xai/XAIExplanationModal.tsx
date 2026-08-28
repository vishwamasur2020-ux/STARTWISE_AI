/**
 * STARTWISE AI — Explainable AI (XAI) Modal Component (Stage 13)
 * Interactive deep-dive modal detailing SHAP feature attribution,
 * positive/negative drivers, multi-model breakdown, and ML architecture transparency.
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  TrendingUp,
  ShieldAlert,
  Target,
  DollarSign,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  Layers,
  BarChart3,
  HelpCircle,
} from 'lucide-react'

import { Modal } from '@/components/ui/Modal'
import { FeatureImpactChart } from './FeatureImpactChart'
import { useCombinedExplanation } from '@/hooks/useExplainability'
import type { FactorItem, SingleModelExplanationResponse } from '@/types/explainability'

interface XAIExplanationModalProps {
  isOpen: boolean
  onClose: () => void
  predictionId?: string
  businessName?: string
}

type XAITab = 'overview' | 'success' | 'risk' | 'roi' | 'competition' | 'pipeline'

export function XAIExplanationModal({
  isOpen,
  onClose,
  predictionId,
  businessName,
}: XAIExplanationModalProps) {
  const [activeTab, setActiveTab] = useState<XAITab>('overview')

  const { data: explanation, isLoading, error } = useCombinedExplanation(
    predictionId,
    isOpen
  )

  const tabs: { id: XAITab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Decision Summary', icon: <Sparkles className="h-4 w-4" /> },
    { id: 'success', label: 'Success Model', icon: <TrendingUp className="h-4 w-4" /> },
    { id: 'risk', label: 'Risk Drivers', icon: <ShieldAlert className="h-4 w-4" /> },
    { id: 'roi', label: 'ROI Factors', icon: <DollarSign className="h-4 w-4" /> },
    { id: 'competition', label: 'Competition', icon: <Target className="h-4 w-4" /> },
    { id: 'pipeline', label: 'How It Works', icon: <Layers className="h-4 w-4" /> },
  ]

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Explainable AI (XAI) Decision Insights"
      description={`${businessName || explanation?.business_name || 'Startup Concept Analysis'} — SHAP Attribution & Model Interpretability`}
      maxWidth="xl"
    >
      <div className="space-y-6 pt-2">
        {/* ── Navigation Tabs ───────────────────────────────────────────────── */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 border-b border-slate-200/80 dark:border-white/10 scrollbar-none">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-zinc-800/60'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>

        {/* ── Loading Skeleton ──────────────────────────────────────────────── */}
        {isLoading && (
          <div className="py-12 space-y-4 animate-pulse">
            <div className="h-20 bg-slate-200 dark:bg-zinc-800 rounded-2xl" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="h-44 bg-slate-200 dark:bg-zinc-800 rounded-2xl" />
              <div className="h-44 bg-slate-200 dark:bg-zinc-800 rounded-2xl" />
            </div>
            <div className="h-56 bg-slate-200 dark:bg-zinc-800 rounded-2xl" />
          </div>
        )}

        {/* ── Error State ──────────────────────────────────────────────────── */}
        {!isLoading && error && (
          <div className="p-8 text-center space-y-3 bg-rose-500/10 border border-rose-500/20 rounded-2xl">
            <AlertTriangle className="h-8 w-8 text-rose-500 mx-auto" />
            <h4 className="font-bold text-slate-900 dark:text-white">Explanation Unavailable</h4>
            <p className="text-xs text-slate-500 dark:text-zinc-400 max-w-md mx-auto">
              We were unable to calculate SHAP feature attributions for this prediction at this time.
            </p>
          </div>
        )}

        {/* ── Tab Content ──────────────────────────────────────────────────── */}
        {!isLoading && explanation && (
          <AnimatePresence mode="wait">
            {activeTab === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="space-y-6"
              >
                {/* Decision Narrative Summary */}
                <div className="p-5 rounded-2xl bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-indigo-500/10 border border-cyan-500/20 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider">
                    <Sparkles className="h-4 w-4" /> AI Decision Narrative
                  </div>
                  <p className="text-sm text-slate-700 dark:text-zinc-200 leading-relaxed font-medium">
                    {explanation.overall_decision_summary}
                  </p>
                </div>

                {/* Top Positive & Negative Factor Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Positive Factors */}
                  <div className="p-5 rounded-2xl bg-emerald-500/5 dark:bg-emerald-950/20 border border-emerald-500/20 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
                      <CheckCircle2 className="h-4 w-4" /> Primary Positive Contributors
                    </div>
                    <div className="space-y-2">
                      {explanation.top_positive_factors.slice(0, 3).map((f, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 text-xs text-slate-700 dark:text-zinc-300"
                        >
                          <span className="font-bold text-emerald-500 mt-0.5">✓</span>
                          <div className="space-y-0.5">
                            <span className="font-semibold text-slate-900 dark:text-white">
                              {f.display_name}
                            </span>
                            <p className="text-[11px] text-slate-500 dark:text-zinc-400 leading-normal">
                              {f.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Negative Factors */}
                  <div className="p-5 rounded-2xl bg-rose-500/5 dark:bg-rose-950/20 border border-rose-500/20 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider">
                      <AlertTriangle className="h-4 w-4" /> Key Resistance Factors
                    </div>
                    <div className="space-y-2">
                      {explanation.top_negative_factors.slice(0, 3).map((f, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 text-xs text-slate-700 dark:text-zinc-300"
                        >
                          <span className="font-bold text-rose-500 mt-0.5">⚠</span>
                          <div className="space-y-0.5">
                            <span className="font-semibold text-slate-900 dark:text-white">
                              {f.display_name}
                            </span>
                            <p className="text-[11px] text-slate-500 dark:text-zinc-400 leading-normal">
                              {f.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Overall SHAP Impact Horizontal Chart */}
                <div className="p-5 rounded-2xl bg-slate-50 dark:bg-zinc-900/60 border border-slate-200/80 dark:border-zinc-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="h-4 w-4 text-cyan-500" />
                      <h4 className="font-bold text-slate-900 dark:text-white text-sm">
                        Global SHAP Impact Attribution (Success Model)
                      </h4>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Game-Theoretic Shapley Values
                    </span>
                  </div>
                  <FeatureImpactChart
                    features={explanation.success.feature_contributions}
                    maxItems={7}
                    height={240}
                  />
                </div>
              </motion.div>
            )}

            {activeTab === 'success' && (
              <ModelExplanationTab explanation={explanation.success} />
            )}

            {activeTab === 'risk' && (
              <ModelExplanationTab explanation={explanation.risk} />
            )}

            {activeTab === 'roi' && (
              <ModelExplanationTab explanation={explanation.roi} />
            )}

            {activeTab === 'competition' && (
              <ModelExplanationTab explanation={explanation.competition} />
            )}

            {activeTab === 'pipeline' && (
              <motion.div
                key="pipeline"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="space-y-6"
              >
                <div className="space-y-1">
                  <h4 className="font-black text-slate-900 dark:text-white text-base">
                    How STARTWISE AI Generates Predictions & Explanations
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-zinc-400">
                    Transparent, verifiable 5-stage Machine Learning & Explainable AI pipeline.
                  </p>
                </div>

                <div className="grid grid-cols-1 gap-3">
                  {explanation.pipeline_steps.map((step) => (
                    <div
                      key={step.step_number}
                      className="flex items-start gap-3.5 p-4 rounded-2xl bg-slate-50 dark:bg-zinc-900/60 border border-slate-200/80 dark:border-zinc-800"
                    >
                      <div className="h-7 w-7 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center text-xs font-black flex-shrink-0 mt-0.5">
                        {step.step_number}
                      </div>
                      <div className="space-y-1">
                        <h5 className="font-bold text-slate-900 dark:text-white text-xs">
                          {step.title}
                        </h5>
                        <p className="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed">
                          {step.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        )}

        {/* ── Responsible AI Non-Causation Disclaimer ───────────────────────── */}
        <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-slate-100 dark:bg-zinc-800/60 text-slate-500 dark:text-zinc-400 text-[11px] leading-relaxed border border-slate-200 dark:border-zinc-700/60">
          <HelpCircle className="h-4 w-4 text-slate-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Explainability Disclaimer:</strong> These explanations describe which model
            features influenced the calculated statistical prediction based on historical training
            patterns. They do not prove that a feature directly causes a specific business outcome.
          </span>
        </div>
      </div>
    </Modal>
  )
}

function ModelExplanationTab({
  explanation,
}: {
  explanation: SingleModelExplanationResponse
}) {
  return (
    <motion.div
      key={explanation.model_name}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      className="space-y-6"
    >
      {/* Model Header & Stats */}
      <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 dark:bg-zinc-900/60 border border-slate-200/80 dark:border-zinc-800 flex-wrap gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-cyan-500" />
            <h4 className="font-bold text-slate-900 dark:text-white text-sm">
              {explanation.model_info.model_name} ({explanation.model_info.algorithm})
            </h4>
          </div>
          <p className="text-xs text-slate-500 dark:text-zinc-400">
            Method: {explanation.model_info.explanation_method} · Evaluated {explanation.model_info.features_used} Features
          </p>
        </div>
        <div className="text-right">
          <span className="text-[10px] uppercase font-bold text-slate-400 block">
            {explanation.target_metric}
          </span>
          <span className="text-lg font-black text-cyan-600 dark:text-cyan-400">
            {typeof explanation.predicted_value === 'boolean'
              ? explanation.predicted_value
                ? 'High Potential'
                : 'Moderate'
              : String(explanation.predicted_value)}
            {explanation.probability !== null && explanation.probability !== undefined && (
              <span className="text-xs text-slate-400 ml-1">({explanation.probability.toFixed(1)}%)</span>
            )}
          </span>
        </div>
      </div>

      {/* Model Narrative Summary */}
      <div className="p-4 rounded-2xl bg-cyan-500/5 dark:bg-cyan-950/20 border border-cyan-500/20">
        <p className="text-xs text-slate-700 dark:text-zinc-300 leading-relaxed font-medium">
          {explanation.summary}
        </p>
      </div>

      {/* Positive & Negative Drivers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 space-y-2.5">
          <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5" /> Positive Drivers
          </span>
          <div className="space-y-1.5">
            {explanation.top_positive_factors.length > 0 ? (
              explanation.top_positive_factors.map((f, i) => (
                <FactorRow key={i} factor={f} isPos={true} />
              ))
            ) : (
              <p className="text-[11px] text-slate-400 italic">No significant positive drivers.</p>
            )}
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-rose-500/5 border border-rose-500/20 space-y-2.5">
          <span className="text-xs font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="h-3.5 w-3.5" /> Resistance Factors
          </span>
          <div className="space-y-1.5">
            {explanation.top_negative_factors.length > 0 ? (
              explanation.top_negative_factors.map((f, i) => (
                <FactorRow key={i} factor={f} isPos={false} />
              ))
            ) : (
              <p className="text-[11px] text-slate-400 italic">No significant resistance factors.</p>
            )}
          </div>
        </div>
      </div>

      {/* SHAP Feature Contribution Chart */}
      <div className="p-5 rounded-2xl bg-slate-50 dark:bg-zinc-900/60 border border-slate-200/80 dark:border-zinc-800 space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-wider">
            Feature Attribution Impact Breakdown
          </h4>
          <span className="text-[10px] text-slate-400 font-mono">
            {explanation.model_info.explanation_method}
          </span>
        </div>
        <FeatureImpactChart features={explanation.feature_contributions} maxItems={8} height={260} />
      </div>
    </motion.div>
  )
}

function FactorRow({ factor, isPos }: { factor: FactorItem; isPos: boolean }) {
  return (
    <div className="flex items-start justify-between gap-2 text-xs py-1 border-b border-slate-200/40 dark:border-zinc-800/60 last:border-0">
      <div className="space-y-0.5">
        <span className="font-semibold text-slate-800 dark:text-zinc-200 block">
          {factor.display_name}
        </span>
        <p className="text-[10px] text-slate-500 dark:text-zinc-400">{factor.description}</p>
      </div>
      <span
        className={`font-mono text-xs font-bold whitespace-nowrap ${
          isPos ? 'text-emerald-500' : 'text-rose-500'
        }`}
      >
        {isPos ? '+' : ''}
        {factor.impact.toFixed(3)}
      </span>
    </div>
  )
}
