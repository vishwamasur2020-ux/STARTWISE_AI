/**
 * STARTWISE AI — My Startup Ideas History Catalog
 * Catalog with live search bar, category filters, sorting dropdown, pagination, glass cards, and delete modal.
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  BrainCircuit,
  Search,
  Plus,
  ArrowRight,
  Trash2,
  Edit,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { GlassCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useStartups, useDeleteStartup } from '@/hooks/useStartups'
import { StartupIdea } from '@/types/startup'

const CATEGORIES = ['All', 'Food', 'Retail', 'Technology', 'Healthcare', 'Education', 'Services']

export default function StartupHistoryPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'highest_investment' | 'lowest_investment' | 'alphabetical'>('newest')
  const [page, setPage] = useState(1)
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null)

  const { data, isLoading } = useStartups({
    query: searchQuery || undefined,
    category: selectedCategory !== 'All' ? selectedCategory : undefined,
    sort_by: sortBy,
    page,
    per_page: 9,
  })

  const deleteMutation = useDeleteStartup()

  const handleDeleteConfirm = () => {
    if (!deleteTargetId) return
    deleteMutation.mutate(deleteTargetId, {
      onSuccess: () => setDeleteTargetId(null),
    })
  }

  const startups = data?.items || []
  const totalPages = data?.pages || 1

  return (
    <div className="space-y-8 pb-16">
      <Breadcrumb items={[{ label: 'AI Validation', href: '/startup-validation' }, { label: 'My Startup Ideas' }]} />

      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            <BrainCircuit className="h-4 w-4" /> Validated Portfolio
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">My Startup Ideas</h1>
        </div>

        <Link to="/startup-validation/new">
          <Button
            size="sm"
            leftIcon={<Plus className="h-4 w-4" />}
            className="bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold rounded-xl shadow-md text-xs"
          >
            Create New Startup
          </Button>
        </Link>
      </div>

      {/* Search & Filter Bar */}
      <GlassCard className="p-4 sm:p-6 space-y-4">
        <div className="flex flex-col md:flex-row items-center gap-4">
          <div className="flex-1 w-full">
            <Input
              type="text"
              placeholder="Search startup name, location, or description..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setPage(1)
              }}
              leftIcon={<Search className="h-4 w-4 text-slate-400" />}
              id="history-search"
            />
          </div>

          <div className="w-full md:w-64">
            <Select
              label=""
              options={[
                { label: 'Sort: Newest First', value: 'newest' },
                { label: 'Sort: Oldest First', value: 'oldest' },
                { label: 'Sort: Highest Investment', value: 'highest_investment' },
                { label: 'Sort: Lowest Investment', value: 'lowest_investment' },
                { label: 'Sort: Alphabetical (A-Z)', value: 'alphabetical' },
              ]}
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
            />
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 dark:border-zinc-800">
          <span className="text-xs font-bold text-slate-400 mr-2 flex items-center gap-1">
            <Filter className="h-3.5 w-3.5" /> Category:
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => {
                setSelectedCategory(cat)
                setPage(1)
              }}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                selectedCategory === cat
                  ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md'
                  : 'bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </GlassCard>

      {/* Startup Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-64 w-full rounded-3xl" />
          ))}
        </div>
      ) : startups.length === 0 ? (
        <EmptyState
          title="No Startup Ideas Found"
          description={
            searchQuery || selectedCategory !== 'All'
              ? 'No startup concepts match your current search query or category filter.'
              : 'You have not submitted any startup ideas yet. Start by validating your first concept!'
          }
          action={
            <Link to="/startup-validation/new">
              <Button size="sm" className="bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold rounded-xl text-xs">
                Validate Your First Idea
              </Button>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {startups.map((item: StartupIdea) => (
            <motion.div key={item.id} whileHover={{ y: -4 }}>
              <GlassCard className="p-6 space-y-4 h-full flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-widest text-cyan-600 dark:text-cyan-400">
                        {item.business_category}
                      </span>
                      <h3 className="text-lg font-bold text-slate-900 dark:text-white truncate">{item.business_name}</h3>
                    </div>
                    <Badge variant="primary" size="sm">
                      {item.competition_level || 'Medium'} Risk
                    </Badge>
                  </div>

                  <p className="text-xs text-slate-500 dark:text-zinc-400 line-clamp-2 leading-relaxed">
                    {item.description || 'No description provided.'}
                  </p>

                  <div className="grid grid-cols-2 gap-2 p-3 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 text-xs">
                    <div>
                      <span className="text-[10px] text-slate-400">Capital Investment</span>
                      <p className="font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">₹{item.investment_amount?.toLocaleString()}</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 font-medium">Location</span>
                      <p className="font-bold text-slate-800 dark:text-zinc-200 mt-0.5 truncate">{item.preferred_location}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-zinc-800 text-xs">
                  <Link to={`/startup-validation/${item.id}`} className="font-semibold text-cyan-600 dark:text-cyan-400 hover:underline flex items-center gap-1">
                    View Details <ArrowRight className="h-3.5 w-3.5" />
                  </Link>

                  <div className="flex items-center gap-2">
                    <Link to={`/startup-validation/edit/${item.id}`}>
                      <button className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-600 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors">
                        <Edit className="h-4 w-4" />
                      </button>
                    </Link>
                    <button
                      onClick={() => setDeleteTargetId(item.id)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}

      {/* Pagination Bar */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-4">
          <Button
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
            disabled={page === 1}
            variant="outline"
            size="sm"
            leftIcon={<ChevronLeft className="h-4 w-4" />}
            className="rounded-xl text-xs"
          >
            Previous
          </Button>

          <span className="text-xs font-semibold text-slate-500">
            Page {page} of {totalPages}
          </span>

          <Button
            onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
            disabled={page === totalPages}
            variant="outline"
            size="sm"
            rightIcon={<ChevronRight className="h-4 w-4" />}
            className="rounded-xl text-xs"
          >
            Next
          </Button>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteTargetId}
        onClose={() => setDeleteTargetId(null)}
        title="Confirm Deletion"
        description="Are you sure you want to delete this startup concept from your portfolio?"
      >
        <div className="flex items-center justify-end gap-3 pt-4">
          <Button onClick={() => setDeleteTargetId(null)} variant="outline" size="sm" className="rounded-xl text-xs">
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
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
