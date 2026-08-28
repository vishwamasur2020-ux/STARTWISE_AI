/**
 * STARTWISE AI — Executive PDF Reports Page Component
 * Catalog of generated PDF reports, instant preview modal, and download actions.
 */

import { useState } from 'react'
import { FileText, Download, Eye, Calendar } from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { GlassCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Modal } from '@/components/ui/Modal'

const MOCK_REPORTS = [
  {
    id: '1',
    title: 'Urban Brew Coffee Lounge — Executive Feasibility Report',
    date: 'August 04, 2026',
    category: 'Food & Beverage',
    score: '91.5%',
    risk: 'Low',
    summary: 'Comprehensive analysis of market demand in Indiranagar, Bengaluru, competitor pricing benchmarks, and 3-year P&L projection.',
  },
  {
    id: '2',
    title: 'Quick Parcel Logistics HUB — Franchise Evaluation',
    date: 'July 28, 2026',
    category: 'Retail & Logistics',
    score: '86.8%',
    risk: 'Low',
    summary: 'Evaluation of DTDC logistics franchise ROI, initial setup capital breakdown, and break-even timeline.',
  },
]

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<any | null>(null)

  const handleDownload = (title: string) => {
    toast.success(`Downloading executive PDF: ${title}`)
  }

  return (
    <div className="space-y-8 pb-12">
      <Breadcrumb items={[{ label: 'Executive PDF Reports' }]} />

      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
          <FileText className="h-4 w-4" /> 1-Click Executive Documentation
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
          Generated PDF Reports
        </h1>
        <p className="text-sm text-slate-500 dark:text-zinc-400 max-w-2xl">
          Download beautifully formatted pitch decks and financial feasibility reports ready for bank loan submissions and angel investor reviews.
        </p>
      </div>

      {/* Reports Grid */}
      <div className="space-y-4">
        {MOCK_REPORTS.map((report) => (
          <GlassCard key={report.id} className="p-6 sm:p-8 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/80 dark:border-zinc-800 pb-4">
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-widest text-cyan-600 dark:text-cyan-400">
                  {report.category}
                </span>
                <h3 className="text-xl font-extrabold text-slate-900 dark:text-white">{report.title}</h3>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Calendar className="h-3.5 w-3.5" /> Generated on {report.date}
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Button
                  onClick={() => setSelectedReport(report)}
                  variant="outline"
                  size="sm"
                  leftIcon={<Eye className="h-4 w-4" />}
                  className="rounded-xl text-xs font-semibold"
                >
                  Preview Report
                </Button>
                <Button
                  onClick={() => handleDownload(report.title)}
                  size="sm"
                  leftIcon={<Download className="h-4 w-4" />}
                  className="bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold rounded-xl text-xs shadow-md"
                >
                  Download PDF
                </Button>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-slate-600 dark:text-zinc-300 leading-relaxed">
              {report.summary}
            </p>
          </GlassCard>
        ))}
      </div>

      {/* Preview Modal */}
      <Modal
        isOpen={!!selectedReport}
        onClose={() => setSelectedReport(null)}
        title={selectedReport?.title || 'Report Preview'}
        maxWidth="lg"
      >
        <div className="space-y-4 text-xs text-slate-700 dark:text-zinc-300">
          <div className="p-4 rounded-2xl bg-cyan-50 dark:bg-cyan-950/40 border border-cyan-200 dark:border-cyan-800 flex items-center justify-between">
            <div>
              <span className="font-bold text-cyan-900 dark:text-cyan-200">AI Feasibility Score</span>
              <p className="text-2xl font-black text-cyan-600 dark:text-cyan-400">{selectedReport?.score}</p>
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold border border-emerald-300">
              {selectedReport?.risk} Risk Profile
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 space-y-2">
            <h4 className="font-bold text-slate-900 dark:text-white">Executive Summary</h4>
            <p className="leading-relaxed text-slate-600 dark:text-zinc-400">
              {selectedReport?.summary}
            </p>
          </div>

          {/* XAI Attribution Summary in PDF Preview */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 space-y-3 border border-slate-200/80 dark:border-zinc-700/80">
            <div className="flex items-center justify-between">
              <h4 className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                <span className="text-cyan-500 font-black">✦</span> Explainable AI (XAI) Attribution
              </h4>
              <span className="text-[10px] text-slate-400 font-mono">SHAP TreeExplainer</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-2.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-1">
                <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
                  ✓ Positive Attribution
                </span>
                <p className="text-[11px] text-slate-600 dark:text-zinc-300">
                  Strong market demand & healthy revenue multiples.
                </p>
              </div>
              <div className="p-2.5 rounded-xl bg-rose-500/5 border border-rose-500/20 space-y-1">
                <span className="text-[10px] font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider">
                  ⚠ Resistance Factors
                </span>
                <p className="text-[11px] text-slate-600 dark:text-zinc-300">
                  Local category density & initial capital payback.
                </p>
              </div>
            </div>
          </div>

          <Button
            onClick={() => {
              if (selectedReport) handleDownload(selectedReport.title)
              setSelectedReport(null)
            }}
            fullWidth
            className="bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold rounded-xl py-3 mt-2"
          >
            Download Complete PDF File
          </Button>
        </div>
      </Modal>
    </div>
  )
}
