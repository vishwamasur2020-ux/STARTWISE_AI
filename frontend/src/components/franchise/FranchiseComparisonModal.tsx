/**
 * STARTWISE AI — Franchise Comparison Modal Component (Stage 8)
 * Side-by-side comparison table for 2 to 4 selected franchises.
 */

import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'
import { FranchiseComparisonResponse } from '@/types/franchise'
import { CheckCircle2, XCircle, DollarSign, TrendingUp, ShieldAlert, Award, MapPin } from 'lucide-react'

interface FranchiseComparisonModalProps {
  isOpen: boolean
  onClose: () => void
  comparisonData: FranchiseComparisonResponse | null
  isLoading?: boolean
}

export function FranchiseComparisonModal({
  isOpen,
  onClose,
  comparisonData,
  isLoading = false,
}: FranchiseComparisonModalProps) {
  if (!comparisonData || isLoading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Side-by-Side Franchise Comparison" maxWidth="xl">
        <div className="p-8 text-center text-slate-500">Loading comparison matrix...</div>
      </Modal>
    )
  }

  const { franchises } = comparisonData

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Side-by-Side Franchise Comparison"
      description="Comparing financial requirements, expected ROI, risk ratings, and operational advantages."
      maxWidth="xl"
    >
      <div className="overflow-x-auto pt-2 pb-4">
        <table className="w-full text-left text-xs border-collapse min-w-[600px]">
          <thead>
            <tr className="border-b border-slate-200/80 dark:border-zinc-800">
              <th className="p-3 font-extrabold text-slate-900 dark:text-white w-1/4">Criteria</th>
              {franchises.map((f) => (
                <th key={f.id} className="p-3 font-black text-cyan-600 dark:text-cyan-400 text-sm">
                  {f.franchise_name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200/60 dark:divide-zinc-800/80">
            {/* Category & Business Model */}
            <tr>
              <td className="p-3 font-semibold text-slate-500 dark:text-zinc-400">Industry / Model</td>
              {franchises.map((f) => (
                <td key={f.id} className="p-3 font-bold text-slate-900 dark:text-white">
                  {f.industry} <span className="text-[10px] text-slate-400">({f.business_model || 'Franchise'})</span>
                </td>
              ))}
            </tr>

            {/* Investment Range */}
            <tr>
              <td className="p-3 font-semibold text-slate-500 dark:text-zinc-400 flex items-center gap-1.5">
                <DollarSign className="h-3.5 w-3.5 text-emerald-500" /> Capital Investment
              </td>
              {franchises.map((f) => (
                <td key={f.id} className="p-3 font-extrabold text-emerald-600 dark:text-emerald-400">
                  ₹{(f.minimum_investment / 100000).toFixed(1)}L - ₹{(f.maximum_investment / 100000).toFixed(1)} Lakh
                </td>
              ))}
            </tr>

            {/* Expected ROI */}
            <tr>
              <td className="p-3 font-semibold text-slate-500 dark:text-zinc-400 flex items-center gap-1.5">
                <TrendingUp className="h-3.5 w-3.5 text-cyan-500" /> Estimated Annual ROI
              </td>
              {franchises.map((f) => (
                <td key={f.id} className="p-3 font-black text-cyan-600 dark:text-cyan-400">
                  {f.roi.toFixed(1)}%
                </td>
              ))}
            </tr>

            {/* Risk Level */}
            <tr>
              <td className="p-3 font-semibold text-slate-500 dark:text-zinc-400 flex items-center gap-1.5">
                <ShieldAlert className="h-3.5 w-3.5 text-amber-500" /> Risk Rating
              </td>
              {franchises.map((f) => (
                <td key={f.id} className="p-3">
                  <Badge variant={f.risk_level.toLowerCase() === 'low' ? 'success' : f.risk_level.toLowerCase() === 'medium' ? 'warning' : 'danger'}>
                    {f.risk_level} Risk
                  </Badge>
                </td>
              ))}
            </tr>

            {/* Location / Headquarters */}
            <tr>
              <td className="p-3 font-semibold text-slate-500 dark:text-zinc-400 flex items-center gap-1.5">
                <MapPin className="h-3.5 w-3.5 text-indigo-500" /> Primary Location
              </td>
              {franchises.map((f) => (
                <td key={f.id} className="p-3 text-slate-700 dark:text-zinc-300">
                  {f.city || 'Nationwide'}, {f.country}
                </td>
              ))}
            </tr>

            {/* Required Experience */}
            <tr>
              <td className="p-3 font-semibold text-slate-500 dark:text-zinc-400 flex items-center gap-1.5">
                <Award className="h-3.5 w-3.5 text-blue-500" /> Experience Required
              </td>
              {franchises.map((f) => (
                <td key={f.id} className="p-3 text-slate-700 dark:text-zinc-300">
                  {f.experience_required === 0 ? 'No prior experience' : `${f.experience_required} Years`}
                </td>
              ))}
            </tr>

            {/* Key Advantages */}
            <tr>
              <td className="p-3 font-semibold text-slate-500 dark:text-zinc-400">Key Advantages</td>
              {franchises.map((f) => (
                <td key={f.id} className="p-3 space-y-1">
                  {(f.advantages || []).map((adv, idx) => (
                    <div key={idx} className="flex items-start gap-1 text-[11px] text-slate-600 dark:text-zinc-300">
                      <CheckCircle2 className="h-3 w-3 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span>{adv}</span>
                    </div>
                  ))}
                </td>
              ))}
            </tr>

            {/* Key Disadvantages */}
            <tr>
              <td className="p-3 font-semibold text-slate-500 dark:text-zinc-400">Considerations</td>
              {franchises.map((f) => (
                <td key={f.id} className="p-3 space-y-1">
                  {(f.disadvantages || []).map((dis, idx) => (
                    <div key={idx} className="flex items-start gap-1 text-[11px] text-slate-500 dark:text-zinc-400">
                      <XCircle className="h-3 w-3 text-rose-500 flex-shrink-0 mt-0.5" />
                      <span>{dis}</span>
                    </div>
                  ))}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </Modal>
  )
}
