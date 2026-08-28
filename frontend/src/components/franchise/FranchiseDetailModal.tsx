/**
 * STARTWISE AI — Franchise Detail Modal Component (Stage 8)
 * Displays full details, feature-level "Why STARTWISE AI Recommended This" breakdown,
 * pros/cons, contact information, and synthetic data disclaimer.
 */

import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { FranchiseRecommendationItem, FranchiseItem } from '@/types/franchise'
import {
  CheckCircle2,
  XCircle,
  ExternalLink,
  Mail,
  Sparkles,
  Info,
} from 'lucide-react'

interface FranchiseDetailModalProps {
  isOpen: boolean
  onClose: () => void
  recommendationItem?: FranchiseRecommendationItem | null
  franchiseItem?: FranchiseItem | null
}

export function FranchiseDetailModal({
  isOpen,
  onClose,
  recommendationItem,
  franchiseItem,
}: FranchiseDetailModalProps) {
  const f = recommendationItem?.franchise || franchiseItem

  if (!f) return null

  const matchScore = recommendationItem?.match_score
  const scoreLabel = recommendationItem?.score_label
  const explanations = recommendationItem?.explanation || []

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={f.franchise_name}
      description={`${f.industry} Franchise Opportunity (${f.business_model || 'Franchise'})`}
      maxWidth="xl"
    >
      <div className="space-y-6 pt-2">
        {/* Match Header Badge if part of recommendation */}
        {matchScore !== undefined && (
          <div className="p-4 rounded-2xl bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-indigo-500/10 border border-cyan-500/20 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-2xl bg-cyan-500 text-white font-black text-lg flex items-center justify-center shadow-lg shadow-cyan-500/30">
                {Math.round(matchScore)}%
              </div>
              <div>
                <Badge variant="primary" className="text-xs">
                  {scoreLabel}
                </Badge>
                <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                  Calculated by NearestNeighbors Cosine Similarity & Domain Weights
                </p>
              </div>
            </div>
            <Sparkles className="h-6 w-6 text-cyan-500 animate-pulse" />
          </div>
        )}

        {/* Why STARTWISE AI Recommended This Section */}
        {explanations.length > 0 && (
          <div className="space-y-3 p-4 rounded-2xl bg-slate-500/5 dark:bg-zinc-800/40 border border-slate-200/80 dark:border-zinc-800">
            <h4 className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="h-4 w-4 text-cyan-500" /> Why STARTWISE AI Recommended This
            </h4>
            <div className="space-y-2 text-xs">
              {explanations.map((exp, idx) => (
                <div key={idx} className="flex items-start gap-2 text-slate-700 dark:text-zinc-300">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                  <span>{exp}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Core Financial & Operational Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
            <span className="text-[11px] text-slate-400 block font-medium">Min Investment</span>
            <strong className="text-sm font-black text-emerald-600 dark:text-emerald-400">
              ₹{(f.minimum_investment / 100000).toFixed(1)} Lakh
            </strong>
          </div>
          <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
            <span className="text-[11px] text-slate-400 block font-medium">Est. Annual ROI</span>
            <strong className="text-sm font-black text-cyan-600 dark:text-cyan-400">
              {f.roi.toFixed(1)}%
            </strong>
          </div>
          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <span className="text-[11px] text-slate-400 block font-medium">Risk Level</span>
            <strong className="text-sm font-black text-amber-600 dark:text-amber-400">
              {f.risk_level}
            </strong>
          </div>
          <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
            <span className="text-[11px] text-slate-400 block font-medium">Primary Location</span>
            <strong className="text-sm font-black text-indigo-600 dark:text-indigo-400">
              {f.city || 'Nationwide'}
            </strong>
          </div>
        </div>

        {/* Overview Description */}
        {f.description && (
          <div className="space-y-1 text-xs">
            <h4 className="font-bold text-slate-900 dark:text-white">Brand Overview</h4>
            <p className="text-slate-600 dark:text-zinc-300 leading-relaxed">{f.description}</p>
          </div>
        )}

        {/* Advantages & Considerations */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-2">
            <h5 className="font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider text-[11px]">
              Key Advantages
            </h5>
            <ul className="space-y-1.5 text-slate-600 dark:text-zinc-300">
              {(f.advantages || ['High profit margin model', 'Turnkey staff training included']).map((adv, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                  <span>{adv}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/20 space-y-2">
            <h5 className="font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider text-[11px]">
              Operational Considerations
            </h5>
            <ul className="space-y-1.5 text-slate-600 dark:text-zinc-300">
              {(f.disadvantages || ['Location footfall dependent', 'Strict brand compliance']).map((dis, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <XCircle className="h-3.5 w-3.5 text-rose-500 flex-shrink-0 mt-0.5" />
                  <span>{dis}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Contact & Website Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-slate-200/80 dark:border-zinc-800 text-xs">
          <div className="flex items-center gap-4 text-slate-500">
            {f.contact_email && (
              <span className="flex items-center gap-1">
                <Mail className="h-3.5 w-3.5 text-cyan-500" /> {f.contact_email}
              </span>
            )}
          </div>

          {f.website && (
            <a href={f.website} target="_blank" rel="noopener noreferrer">
              <Button size="sm" rightIcon={<ExternalLink className="h-3.5 w-3.5" />} className="rounded-xl text-xs">
                Visit Official Website
              </Button>
            </a>
          )}
        </div>

        {/* Disclaimer Note */}
        <div className="flex items-start gap-2 text-[10px] text-slate-400 bg-slate-500/5 p-3 rounded-xl">
          <Info className="h-3.5 w-3.5 flex-shrink-0 mt-0.5 text-cyan-500" />
          <span>
            DEMO / SYNTHETIC DATA: Financial parameters (investment ranges, estimated ROI) are indicative estimates for academic project demonstration.
          </span>
        </div>
      </div>
    </Modal>
  )
}
