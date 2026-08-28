/**
 * STARTWISE AI — AI Franchise Recommendation Engine Page (Stage 8)
 * Full interactive hub for personalized hybrid AI franchise recommendations,
 * catalog search/filters, side-by-side comparison, and detailed match breakdowns.
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Store,
  Sparkles,
  Search,
  SlidersHorizontal,
  CheckCircle2,
  CheckSquare,
  Square,
} from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { GlassCard } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Skeleton } from '@/components/ui/Skeleton'

import {
  useGenerateRecommendations,
  useFranchises,
  useFranchiseCategories,
  useCompareFranchises,
} from '@/hooks/useFranchises'
import {
  FranchiseItem,
  FranchiseRecommendationItem,
  FranchiseRecommendationResponse,
  FranchiseComparisonResponse,
} from '@/types/franchise'
import { FranchiseDetailModal } from '@/components/franchise/FranchiseDetailModal'
import { FranchiseComparisonModal } from '@/components/franchise/FranchiseComparisonModal'

export default function FranchisePage() {
  // Input parameters state
  const [budget, setBudget] = useState<number>(800000)
  const [category, setCategory] = useState<string>('Food')
  const [location, setLocation] = useState<string>('Bengaluru')
  const [riskPref, setRiskPref] = useState<string>('Low')
  const [experienceYears, setExperienceYears] = useState<number>(2)

  // Recommendation & Catalog state
  const [recommendationResult, setRecommendationResult] = useState<FranchiseRecommendationResponse | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('All')

  // Selection & Comparison state
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>([])
  const [comparisonModalOpen, setComparisonModalOpen] = useState(false)
  const [comparisonData, setComparisonData] = useState<FranchiseComparisonResponse | null>(null)

  // Detail Modal state
  const [detailItem, setDetailItem] = useState<{
    rec?: FranchiseRecommendationItem
    raw?: FranchiseItem
  } | null>(null)

  // Hooks
  const recommendMutation = useGenerateRecommendations()
  const compareMutation = useCompareFranchises()
  const { data: categoriesData = [] } = useFranchiseCategories()
  const { data: catalogFranchises = [], isLoading: catalogLoading } = useFranchises({
    category: selectedCategoryFilter !== 'All' ? selectedCategoryFilter : undefined,
    query: searchQuery || undefined,
  })

  // Trigger Recommendation Calculation
  const handleRunRecommendation = () => {
    recommendMutation.mutate(
      {
        budget,
        business_category: category,
        location,
        experience_years: experienceYears,
        risk_preference: riskPref,
        expected_roi: 25,
      },
      {
        onSuccess: (res) => {
          setRecommendationResult(res)
        },
      }
    )
  }

  // Toggle Comparison Selection
  const toggleComparisonSelect = (id: string) => {
    if (selectedForComparison.includes(id)) {
      setSelectedForComparison(selectedForComparison.filter((item) => item !== id))
    } else {
      if (selectedForComparison.length >= 4) {
        toast.error('You can compare a maximum of 4 franchises at once.')
        return
      }
      setSelectedForComparison([...selectedForComparison, id])
    }
  }

  // Handle Run Comparison
  const handleCompareSelected = () => {
    if (selectedForComparison.length < 2) {
      toast.error('Select at least 2 franchises to compare.')
      return
    }
    compareMutation.mutate(selectedForComparison, {
      onSuccess: (res) => {
        setComparisonData(res)
        setComparisonModalOpen(true)
      },
    })
  }

  const bestMatch = recommendationResult?.recommendations[0]

  return (
    <div className="space-y-8 pb-16">
      <Breadcrumb items={[{ label: 'AI Franchise Recommender' }]} />

      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            <Store className="h-4 w-4" /> Hybrid AI Recommendation System
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
            Find Your Ideal Franchise Match
          </h1>
          <p className="text-sm text-slate-500 dark:text-zinc-400 max-w-2xl">
            Our hybrid NearestNeighbors algorithm matches your budget, category, location, and risk profile against 45+ verified brand opportunities.
          </p>
        </div>

        {/* Top Control Button */}
        <Button
          onClick={handleRunRecommendation}
          isLoading={recommendMutation.isPending}
          size="lg"
          rightIcon={<Sparkles className="h-5 w-5" />}
          className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-2xl py-4 shadow-xl shadow-cyan-500/20 flex-shrink-0"
        >
          {recommendationResult ? 'Recalculate AI Match' : 'Run AI Recommendation Engine'}
        </Button>
      </div>

      {/* ── Active Profile Configuration Card ────────────────────────────────── */}
      <GlassCard className="p-6 space-y-4 border border-cyan-500/20">
        <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4 text-cyan-500" />
            <h3 className="font-bold text-slate-900 dark:text-white text-sm">
              Recommendation Parameters
            </h3>
          </div>
          <span className="text-[11px] text-slate-400">Configure parameters to customize matching</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 text-xs">
          <div>
            <label className="text-slate-400 font-semibold block mb-1">Capital Budget (₹)</label>
            <Input
              type="number"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              placeholder="800000"
              className="text-xs font-bold"
            />
          </div>

          <div>
            <label className="text-slate-400 font-semibold block mb-1">Target Category</label>
            <Select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              options={[
                { label: 'Food & Beverage', value: 'Food' },
                { label: 'Retail & E-Commerce', value: 'Retail' },
                { label: 'Education & Training', value: 'Education' },
                { label: 'Healthcare & Pharma', value: 'Healthcare' },
                { label: 'Services & Salon', value: 'Services' },
                { label: 'Logistics', value: 'Logistics' },
                { label: 'Technology', value: 'Technology' },
                { label: 'Automotive', value: 'Automotive' },
                { label: 'Fitness & Gym', value: 'Fitness' },
              ]}
              className="text-xs font-bold"
            />
          </div>

          <div>
            <label className="text-slate-400 font-semibold block mb-1">Preferred City / Location</label>
            <Input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Bengaluru"
              className="text-xs font-bold"
            />
          </div>

          <div>
            <label className="text-slate-400 font-semibold block mb-1">Risk Preference</label>
            <Select
              value={riskPref}
              onChange={(e) => setRiskPref(e.target.value)}
              options={[
                { label: 'Low Risk', value: 'Low' },
                { label: 'Medium Risk', value: 'Medium' },
                { label: 'High Risk', value: 'High' },
              ]}
              className="text-xs font-bold"
            />
          </div>

          <div>
            <label className="text-slate-400 font-semibold block mb-1">Experience (Yrs)</label>
            <Input
              type="number"
              value={experienceYears}
              onChange={(e) => setExperienceYears(Number(e.target.value))}
              placeholder="2"
              className="text-xs font-bold"
            />
          </div>
        </div>
      </GlassCard>

      {/* ── AI Recommendation Results View ───────────────────────────────────── */}
      <AnimatePresence mode="wait">
        {recommendMutation.isPending ? (
          <GlassCard className="p-12 text-center space-y-4">
            <div className="relative w-16 h-16 mx-auto flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-4 border-cyan-500/20 border-t-cyan-500 animate-spin" />
              <Store className="h-8 w-8 text-cyan-500 animate-pulse" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              Matching Franchises for You...
            </h3>
            <p className="text-xs text-slate-500">
              Applying hard constraint filtering, encoding categorical vectors, and calculating NearestNeighbors Cosine Similarity...
            </p>
          </GlassCard>
        ) : recommendationResult ? (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
            {/* 1. Best Match Highlight Banner */}
            {bestMatch && (
              <GlassCard className="p-6 sm:p-8 relative overflow-hidden border border-cyan-500/30 bg-gradient-to-br from-cyan-500/5 via-blue-500/5 to-transparent">
                <div className="absolute top-0 right-0 px-4 py-1.5 rounded-bl-2xl bg-cyan-500 text-white font-extrabold text-[11px] uppercase tracking-widest flex items-center gap-1">
                  <Sparkles className="h-3.5 w-3.5" /> #1 BEST MATCH
                </div>

                <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                  <div className="flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
                    {/* Score Circle */}
                    <div className="h-28 w-28 rounded-3xl bg-cyan-500 text-white font-black text-3xl flex flex-col items-center justify-center shadow-xl shadow-cyan-500/30 flex-shrink-0">
                      <span>{Math.round(bestMatch.match_score)}%</span>
                      <span className="text-[10px] font-bold tracking-widest uppercase opacity-80">Match</span>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-center sm:justify-start gap-2">
                        <Badge variant="primary">{bestMatch.score_label}</Badge>
                        <Badge variant="secondary">{bestMatch.franchise.industry}</Badge>
                      </div>
                      <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
                        {bestMatch.franchise.franchise_name}
                      </h2>
                      <p className="text-xs text-slate-500 dark:text-zinc-400 max-w-xl">
                        {bestMatch.franchise.description}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
                    <Button
                      onClick={() => setDetailItem({ rec: bestMatch })}
                      size="sm"
                      className="bg-cyan-500 text-white rounded-xl font-bold text-xs w-full sm:w-auto"
                    >
                      View Full Analysis & Contact
                    </Button>
                  </div>
                </div>

                {/* Explanation Bullet Reasons */}
                <div className="mt-6 pt-4 border-t border-slate-200/80 dark:border-zinc-800 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  {bestMatch.explanation.map((reason, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-slate-700 dark:text-zinc-300">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span>{reason}</span>
                    </div>
                  ))}
                </div>
              </GlassCard>
            )}

            {/* 2. Ranked Top Franchises Grid */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-black text-slate-900 dark:text-white">
                  Top Recommended Franchises ({recommendationResult.recommendations.length})
                </h3>

                {selectedForComparison.length > 0 && (
                  <Button
                    onClick={handleCompareSelected}
                    isLoading={compareMutation.isPending}
                    size="sm"
                    className="bg-indigo-600 text-white rounded-xl text-xs font-bold"
                  >
                    Compare Selected ({selectedForComparison.length})
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendationResult.recommendations.map((rec) => {
                  const f = rec.franchise
                  const isSelected = selectedForComparison.includes(f.id)

                  return (
                    <GlassCard
                      key={f.id}
                      className="p-6 space-y-4 relative flex flex-col justify-between border hover:border-cyan-500/40 transition-all cursor-pointer group"
                      onClick={() => setDetailItem({ rec })}
                    >
                      {/* Top Bar: Rank & Checkbox */}
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-400">
                          Rank #{rec.ranking_position}
                        </span>

                        <div className="flex items-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              toggleComparisonSelect(f.id)
                            }}
                            className="text-slate-400 hover:text-cyan-500 transition-colors p-1"
                            title="Select for comparison"
                          >
                            {isSelected ? (
                              <CheckSquare className="h-5 w-5 text-cyan-500" />
                            ) : (
                              <Square className="h-5 w-5" />
                            )}
                          </button>

                          <Badge
                            variant={rec.match_score >= 85 ? 'success' : rec.match_score >= 70 ? 'primary' : 'warning'}
                            className="text-[11px]"
                          >
                            {rec.match_score}% Match
                          </Badge>
                        </div>
                      </div>

                      {/* Brand Info */}
                      <div className="space-y-1">
                        <h4 className="text-lg font-extrabold text-slate-900 dark:text-white group-hover:text-cyan-500 transition-colors">
                          {f.franchise_name}
                        </h4>
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                          <span>{f.industry}</span>
                          <span>•</span>
                          <span>{f.city || 'Nationwide'}</span>
                        </div>
                      </div>

                      {/* Metrics 2-Grid */}
                      <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-200/80 dark:border-zinc-800">
                        <div>
                          <span className="text-[10px] text-slate-400 block">Min Investment</span>
                          <strong className="text-emerald-600 dark:text-emerald-400 font-bold">
                            ₹{(f.minimum_investment / 100000).toFixed(1)} Lakh
                          </strong>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 block">Est. Annual ROI</span>
                          <strong className="text-cyan-600 dark:text-cyan-400 font-bold">
                            {f.roi.toFixed(1)}%
                          </strong>
                        </div>
                      </div>

                      {/* Reasons */}
                      <div className="text-[11px] text-slate-600 dark:text-zinc-400 space-y-1 line-clamp-2">
                        {rec.explanation[0]}
                      </div>
                    </GlassCard>
                  )
                })}
              </div>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>

      {/* ── Browse All Franchises Catalog Section ────────────────────────────── */}
      <div className="space-y-6 pt-8 border-t border-slate-200/80 dark:border-zinc-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-2xl font-black text-slate-900 dark:text-white">
              Explore Franchise Catalog
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400">
              Browse all 45 verified franchise opportunities across categories.
            </p>
          </div>

          {/* Search & Filters */}
          <div className="flex flex-wrap items-center gap-3">
            <Input
              type="text"
              placeholder="Search by brand name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-slate-400" />}
              className="w-48 text-xs"
            />

            <Select
              value={selectedCategoryFilter}
              onChange={(e) => setSelectedCategoryFilter(e.target.value)}
              options={[
                { label: 'All Categories', value: 'All' },
                ...categoriesData.map((c) => ({ label: c, value: c })),
              ]}
              className="text-xs"
            />
          </div>
        </div>

        {/* Catalog Grid */}
        {catalogLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-48 w-full rounded-2xl" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {catalogFranchises.map((f) => (
              <GlassCard
                key={f.id}
                className="p-5 space-y-3 cursor-pointer hover:border-cyan-500/40 transition-all"
                onClick={() => setDetailItem({ raw: f })}
              >
                <div className="flex items-center justify-between">
                  <Badge variant="secondary" className="text-[10px]">
                    {f.industry}
                  </Badge>
                  <span className="text-[11px] text-slate-400">{f.city || 'Nationwide'}</span>
                </div>

                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  {f.franchise_name}
                </h4>

                <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-200/80 dark:border-zinc-800">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Investment</span>
                    <strong className="text-emerald-600 dark:text-emerald-400 font-bold">
                      ₹{(f.minimum_investment / 100000).toFixed(1)}L - ₹{(f.maximum_investment / 100000).toFixed(1)}L
                    </strong>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">ROI</span>
                    <strong className="text-cyan-600 dark:text-cyan-400 font-bold">
                      {f.roi}%
                    </strong>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        )}
      </div>

      {/* ── Modals ───────────────────────────────────────────────────────────── */}
      {/* Detail Modal */}
      <FranchiseDetailModal
        isOpen={!!detailItem}
        onClose={() => setDetailItem(null)}
        recommendationItem={detailItem?.rec}
        franchiseItem={detailItem?.raw}
      />

      {/* Comparison Modal */}
      <FranchiseComparisonModal
        isOpen={comparisonModalOpen}
        onClose={() => setComparisonModalOpen(false)}
        comparisonData={comparisonData}
        isLoading={compareMutation.isPending}
      />
    </div>
  )
}
