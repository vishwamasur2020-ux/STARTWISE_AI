/**
 * STARTWISE AI — Embeddable XAI Card (Stage 13)
 * Displays top positive/negative factors and a "Why this result?" modal trigger.
 */

import { useState } from 'react'
import { Sparkles, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react'
import { GlassCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { XAIExplanationModal } from './XAIExplanationModal'
import { useCombinedExplanation } from '@/hooks/useExplainability'

interface XAIExplanationCardProps {
  predictionId?: string
  businessName?: string
  className?: string
}

export function XAIExplanationCard({
  predictionId,
  businessName,
  className = '',
}: XAIExplanationCardProps) {
  const [modalOpen, setModalOpen] = useState(false)
  const { data: xai, isLoading } = useCombinedExplanation(predictionId, !!predictionId)

  if (!predictionId) return null

  return (
    <>
      <GlassCard className={`p-6 space-y-4 border border-cyan-500/20 ${className}`}>
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 dark:text-white text-sm">
                Why this result? (XAI Insights)
              </h4>
              <p className="text-xs text-slate-500 dark:text-zinc-400">
                Key model features driving this feasibility assessment
              </p>
            </div>
          </div>

          <Button
            onClick={() => setModalOpen(true)}
            size="sm"
            variant="outline"
            rightIcon={<ArrowRight className="h-3.5 w-3.5" />}
            className="rounded-xl text-xs font-semibold text-cyan-600 dark:text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/10"
          >
            View Full Explanation
          </Button>
        </div>

        {isLoading ? (
          <div className="h-20 bg-slate-200 dark:bg-zinc-800 rounded-xl animate-pulse" />
        ) : xai ? (
          <div className="space-y-3">
            <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed font-medium">
              {xai.overall_decision_summary}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-1.5">
                <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" /> Top Positive Factors
                </span>
                {xai.top_positive_factors.slice(0, 2).map((f, i) => (
                  <div key={i} className="text-xs text-slate-700 dark:text-zinc-300 flex items-center gap-1.5">
                    <span className="text-emerald-500 font-bold">✓</span>
                    <span className="font-medium truncate">{f.display_name}</span>
                  </div>
                ))}
              </div>

              <div className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/20 space-y-1.5">
                <span className="text-[10px] font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" /> Key Resistance Factors
                </span>
                {xai.top_negative_factors.slice(0, 2).map((f, i) => (
                  <div key={i} className="text-xs text-slate-700 dark:text-zinc-300 flex items-center gap-1.5">
                    <span className="text-rose-500 font-bold">⚠</span>
                    <span className="font-medium truncate">{f.display_name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </GlassCard>

      <XAIExplanationModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        predictionId={predictionId}
        businessName={businessName}
      />
    </>
  )
}
