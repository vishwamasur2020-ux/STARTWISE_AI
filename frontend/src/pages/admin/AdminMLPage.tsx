/**
 * STARTWISE AI — Admin ML Model Monitoring Page (Stage 12)
 */

import { RefreshCw, CheckCircle2, AlertTriangle, XCircle, Brain, Cpu } from 'lucide-react'
import { useAdminML } from '@/hooks/useAdmin'

function StatusIcon({ status }: { status: string }) {
  if (status === 'healthy' || status === 'loaded') return <CheckCircle2 className="h-5 w-5 text-green-400" />
  if (status === 'degraded' || status === 'not_loaded') return <AlertTriangle className="h-5 w-5 text-amber-400" />
  return <XCircle className="h-5 w-5 text-red-400" />
}

function StatusBadge({ status }: { status: string }) {
  const colors = {
    healthy: 'bg-green-500/10 text-green-400 border-green-500/30',
    loaded: 'bg-green-500/10 text-green-400 border-green-500/30',
    degraded: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    not_loaded: 'bg-red-500/10 text-red-400 border-red-500/30',
    unavailable: 'bg-red-500/10 text-red-400 border-red-500/30',
  }
  return (
    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${colors[status as keyof typeof colors] || 'bg-slate-700 text-slate-400 border-white/10'}`}>
      {status.replace('_', ' ').toUpperCase()}
    </span>
  )
}

export default function AdminMLPage() {
  const { data, isLoading, refetch, isFetching } = useAdminML()
  const ml = data as any

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white">ML Model Monitoring</h1>
          <p className="text-sm text-slate-400 mt-1">
            {isLoading ? 'Loading…' : ml?.is_fully_loaded ? '✅ All models are loaded and ready for inference.' : '⚠️ Some models are not loaded.'}
          </p>
        </div>
        <button onClick={() => refetch()} disabled={isFetching} className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-white/10 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-700 transition-colors">
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* Artifacts Dir */}
      {!isLoading && ml?.artifacts_dir && (
        <div className="px-4 py-3 bg-slate-800/60 border border-white/10 rounded-xl text-xs text-slate-400 font-mono">
          📂 Artifacts: {ml.artifacts_dir}
        </div>
      )}

      {/* ML Models */}
      <div>
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Trained Models</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {isLoading ? (
            Array.from({ length: 4 }).map((_, i) => <div key={i} className="bg-slate-900 border border-white/10 rounded-2xl p-5 animate-pulse h-28" />)
          ) : (
            ml?.models?.map((m: any) => (
              <div key={m.name} className="bg-slate-900 border border-white/10 rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Brain className="h-4 w-4 text-violet-400" />
                    <span className="text-xs font-bold text-white">{m.name}</span>
                  </div>
                  <StatusIcon status={m.status} />
                </div>
                {m.algorithm && <p className="text-[10px] text-slate-500">{m.algorithm}</p>}
                <div className="flex items-center justify-between">
                  <StatusBadge status={m.status} />
                  <span className="text-[10px] text-slate-600">v{m.version}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Preprocessors */}
      <div>
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Preprocessors</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {isLoading ? (
            Array.from({ length: 4 }).map((_, i) => <div key={i} className="bg-slate-900 border border-white/10 rounded-2xl p-5 animate-pulse h-28" />)
          ) : (
            ml?.preprocessors?.map((p: any) => (
              <div key={p.name} className="bg-slate-900 border border-white/10 rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-cyan-400" />
                    <span className="text-xs font-bold text-white">{p.name}</span>
                  </div>
                  <StatusIcon status={p.status} />
                </div>
                {p.algorithm && <p className="text-[10px] text-slate-500">{p.algorithm}</p>}
                <StatusBadge status={p.status} />
              </div>
            ))
          )}
        </div>
      </div>

      {/* Services Health */}
      <div>
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Service Health</h2>
        <div className="bg-slate-900 border border-white/10 rounded-2xl overflow-hidden">
          {isLoading ? (
            <div className="p-6 animate-pulse space-y-4">
              {Array.from({ length: 5 }).map((_, i) => <div key={i} className="h-8 bg-slate-800 rounded" />)}
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {ml?.services?.map((s: any) => (
                <div key={s.name} className="flex items-center justify-between px-5 py-3.5">
                  <div className="flex items-center gap-3">
                    <StatusIcon status={s.status} />
                    <span className="text-sm font-semibold text-white">{s.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {s.message && <span className="text-xs text-slate-500 hidden md:block">{s.message}</span>}
                    <StatusBadge status={s.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Explainable AI (XAI) Engine Status */}
      <div>
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Explainable AI (XAI) Engine</h2>
        <div className="bg-slate-900 border border-white/10 rounded-2xl p-5 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-white/5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">SHAP TreeExplainer</span>
                <CheckCircle2 className="h-4 w-4 text-green-400" />
              </div>
              <p className="text-[10px] text-slate-400">Success, Risk, & Competition Models</p>
              <span className="text-[10px] font-mono text-green-400 font-semibold block">v0.52.0 Active</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-white/5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">SHAP LinearExplainer</span>
                <CheckCircle2 className="h-4 w-4 text-green-400" />
              </div>
              <p className="text-[10px] text-slate-400">ROI Regression Model</p>
              <span className="text-[10px] font-mono text-green-400 font-semibold block">Independent Masker</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-white/5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">Feature Grouping</span>
                <CheckCircle2 className="h-4 w-4 text-green-400" />
              </div>
              <p className="text-[10px] text-slate-400">One-Hot Category Aggregator</p>
              <span className="text-[10px] font-mono text-cyan-400 font-semibold block">Business Mapped</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-white/5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">Explanation Caching</span>
                <CheckCircle2 className="h-4 w-4 text-green-400" />
              </div>
              <p className="text-[10px] text-slate-400">PostgreSQL Cache Table</p>
              <span className="text-[10px] font-mono text-indigo-400 font-semibold block">prediction_explanations</span>
            </div>
          </div>
        </div>
      </div>

      {/* Model Metrics */}
      {!isLoading && ml?.metrics && Object.keys(ml.metrics).length > 0 && (
        <div>
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Model Metrics (from artifacts)</h2>
          <div className="bg-slate-900 border border-white/10 rounded-2xl p-5">
            <pre className="text-xs text-slate-400 font-mono overflow-auto max-h-64 whitespace-pre-wrap">
              {JSON.stringify(ml.metrics, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Note */}
      <div className="flex items-start gap-2 px-4 py-3 bg-blue-500/10 border border-blue-500/30 rounded-xl text-xs text-blue-400">
        <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
        <span><strong>Admin Note:</strong> ML prediction values are read-only. They are generated by the trained models and cannot be manually modified. Model retraining is done through the offline ML training pipeline only.</span>
      </div>
    </div>
  )
}
