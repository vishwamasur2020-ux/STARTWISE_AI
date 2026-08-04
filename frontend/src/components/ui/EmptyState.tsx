/**
 * STARTWISE AI — Empty State Component
 */

import { ReactNode } from 'react'
import { Sparkles } from 'lucide-react'

export interface EmptyStateProps {
  title: string
  description: string
  icon?: ReactNode
  action?: ReactNode
  className?: string
}

export function EmptyState({
  title,
  description,
  icon,
  action,
  className = '',
}: EmptyStateProps) {
  return (
    <div
      className={`glass-card p-8 sm:p-12 text-center rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/60 dark:bg-zinc-900/60 backdrop-blur-xl flex flex-col items-center justify-center max-w-lg mx-auto ${className}`}
    >
      <div className="h-16 w-16 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mb-4 shadow-sm">
        {icon || <Sparkles className="h-8 w-8" />}
      </div>
      <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-zinc-400 leading-relaxed mb-6">
        {description}
      </p>
      {action && <div>{action}</div>}
    </div>
  )
}
