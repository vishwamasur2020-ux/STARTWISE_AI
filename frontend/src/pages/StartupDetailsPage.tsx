/**
 * STARTWISE AI — Startup Details Page Component
 * Detailed view displaying business, financial, and market parameters alongside AI score placeholders.
 */

import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  Building2,
  MapPin,
  DollarSign,
  Edit,
  Trash2,
  Calendar,
  BrainCircuit,
} from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { GlassCard, AIResultCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Modal } from '@/components/ui/Modal'
import { Skeleton } from '@/components/ui/Skeleton'
import { useStartupDetails, useDeleteStartup } from '@/hooks/useStartups'

export default function StartupDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)

  const { data: startup, isLoading } = useStartupDetails(id || '')
  const deleteMutation = useDeleteStartup()

  const handleDelete = () => {
    if (!id) return
    deleteMutation.mutate(id, {
      onSuccess: () => {
        setDeleteModalOpen(false)
        navigate('/startup-validation/history')
      },
    })
  }

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-8">
        <Skeleton className="h-8 w-64 rounded-xl" />
        <Skeleton className="h-48 w-full rounded-3xl" />
        <Skeleton className="h-64 w-full rounded-3xl" />
      </div>
    )
  }

  if (!startup) {
    return (
      <div className="text-center py-16 space-y-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Startup Idea Not Found</h2>
        <p className="text-xs text-slate-500">The requested startup concept does not exist or was deleted.</p>
        <Link to="/startup-validation/history">
          <Button size="sm" className="bg-cyan-500 text-white rounded-xl">View My Startup Ideas</Button>
        </Link>
      </div>
    )
  }

  const createdDate = new Date(startup.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="space-y-8 pb-16 max-w-4xl mx-auto">
      <Breadcrumb
        items={[
          { label: 'AI Validation', href: '/startup-validation' },
          { label: 'My Startups', href: '/startup-validation/history' },
          { label: startup.business_name },
        ]}
      />

      {/* Title & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/80 dark:border-zinc-800 pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            <BrainCircuit className="h-4 w-4" /> AI Validated Concept
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">{startup.business_name}</h1>
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="font-semibold text-slate-700 dark:text-zinc-300">{startup.business_category}</span>
            <span>•</span>
            <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" /> {createdDate}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link to={`/startup-validation/edit/${startup.id}`}>
            <Button variant="outline" size="sm" leftIcon={<Edit className="h-4 w-4 text-cyan-500" />} className="rounded-xl text-xs font-semibold">
              Edit Idea
            </Button>
          </Link>
          <Button
            onClick={() => setDeleteModalOpen(true)}
            variant="outline"
            size="sm"
            leftIcon={<Trash2 className="h-4 w-4 text-rose-500" />}
            className="rounded-xl text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40"
          >
            Delete
          </Button>
        </div>
      </div>

      {/* AI Prediction Placeholder Result Card */}
      <AIResultCard
        score={startup.prediction_result?.success_probability || 91.5}
        riskLevel={startup.prediction_result?.risk_level || 'Low'}
        estimatedRoi={startup.prediction_result?.estimated_roi || 38.4}
        summary="High commercial feasibility score backed by regional market demand and favorable operating margins."
      />

      {/* Parameter Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Business Info */}
        <GlassCard className="p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-200/80 dark:border-zinc-800 pb-3">
            <Building2 className="h-4 w-4 text-cyan-500" />
            <h3 className="font-extrabold text-slate-900 dark:text-white text-sm">Business Identity</h3>
          </div>
          <div className="space-y-2 text-xs">
            <p><span className="text-slate-400">Category:</span> <strong className="text-slate-800 dark:text-zinc-200">{startup.business_category}</strong></p>
            <p><span className="text-slate-400">Model:</span> {startup.business_model}</p>
            <p><span className="text-slate-400">Description:</span> {startup.description || 'N/A'}</p>
          </div>
        </GlassCard>

        {/* Financial Info */}
        <GlassCard className="p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-200/80 dark:border-zinc-800 pb-3">
            <DollarSign className="h-4 w-4 text-emerald-500" />
            <h3 className="font-extrabold text-slate-900 dark:text-white text-sm">Financial Metrics</h3>
          </div>
          <div className="space-y-2 text-xs">
            <p><span className="text-slate-400">Capital Investment:</span> <strong className="text-emerald-600 dark:text-emerald-400">₹{startup.investment_amount?.toLocaleString()}</strong></p>
            <p><span className="text-slate-400">Est. Revenue:</span> ₹{startup.expected_monthly_revenue?.toLocaleString()}/mo</p>
            <p><span className="text-slate-400">Team Size:</span> {startup.employee_count} Members</p>
          </div>
        </GlassCard>

        {/* Market Info */}
        <GlassCard className="p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-200/80 dark:border-zinc-800 pb-3">
            <MapPin className="h-4 w-4 text-indigo-500" />
            <h3 className="font-extrabold text-slate-900 dark:text-white text-sm">Market Context</h3>
          </div>
          <div className="space-y-2 text-xs">
            <p><span className="text-slate-400">Location:</span> <strong className="text-slate-800 dark:text-zinc-200">{startup.preferred_location}</strong></p>
            <p><span className="text-slate-400">Target Segment:</span> {startup.target_customers}</p>
            <p><span className="text-slate-400">Founder Experience:</span> {startup.experience_years} Years</p>
          </div>
        </GlassCard>
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Confirm Startup Deletion"
        description="Are you sure you want to delete this startup idea? This action cannot be undone."
      >
        <div className="flex items-center justify-end gap-3 pt-4">
          <Button onClick={() => setDeleteModalOpen(false)} variant="outline" size="sm" className="rounded-xl text-xs">
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            isLoading={deleteMutation.isPending}
            size="sm"
            className="bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold"
          >
            Delete Permanently
          </Button>
        </div>
      </Modal>
    </div>
  )
}
