/**
 * STARTWISE AI — Card Components
 * Includes GlassCard, StatsCard, PricingCard, and AIResultCard.
 */

import { HTMLAttributes, forwardRef, ReactNode } from 'react'
import { cn } from '@/utils/cn'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'glass' | 'gradient-border' | 'solid' | 'flat'
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  hover?: boolean
}

const variantClasses = {
  glass: 'glass-card border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl rounded-3xl',
  'gradient-border': 'gradient-border p-6 rounded-3xl',
  solid: 'bg-white dark:bg-zinc-900 rounded-3xl border border-slate-200 dark:border-zinc-800 shadow-card',
  flat: 'bg-slate-50 dark:bg-zinc-900/60 rounded-3xl border border-slate-100 dark:border-zinc-800',
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
  xl: 'p-10',
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'glass', padding = 'md', hover = false, className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          variantClasses[variant],
          variant !== 'gradient-border' && paddingClasses[padding],
          hover && 'cursor-pointer hover:-translate-y-1 hover:shadow-card-hover transition-all duration-300',
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

// ── Sub-components ───────────────────────────────────────────────────────────
export const CardHeader = ({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex flex-col gap-1 mb-4', className)} {...props}>
    {children}
  </div>
)

export const CardTitle = ({ className, children, ...props }: HTMLAttributes<HTMLHeadingElement>) => (
  <h3 className={cn('text-lg font-bold text-slate-900 dark:text-white tracking-tight', className)} {...props}>
    {children}
  </h3>
)

export const CardDescription = ({ className, children, ...props }: HTMLAttributes<HTMLParagraphElement>) => (
  <p className={cn('text-sm text-slate-500 dark:text-zinc-400', className)} {...props}>
    {children}
  </p>
)

export const CardContent = ({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('', className)} {...props}>
    {children}
  </div>
)

export const CardFooter = ({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex items-center justify-between mt-4 pt-4 border-t border-slate-100 dark:border-zinc-800', className)} {...props}>
    {children}
  </div>
)

// ── Specialized Glass Card ───────────────────────────────────────────────────
export function GlassCard({ className = '', children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'glass-card p-6 sm:p-8 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl relative overflow-hidden',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// ── Stats Card ───────────────────────────────────────────────────────────────
export interface StatsCardProps {
  title: string
  value: string | number
  change?: string
  trend?: 'up' | 'down' | 'neutral'
  icon?: ReactNode
  description?: string
  className?: string
}

export function StatsCard({
  title,
  value,
  change,
  trend = 'up',
  icon,
  description,
  className = '',
}: StatsCardProps) {
  return (
    <GlassCard className={cn('p-6 space-y-3', className)}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
          {title}
        </span>
        {icon && (
          <div className="h-10 w-10 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shadow-sm">
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between gap-2">
        <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">{value}</h2>
        {change && (
          <span
            className={`text-xs font-bold px-2 py-0.5 rounded-full border ${
              trend === 'up'
                ? 'bg-emerald-100 text-emerald-700 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800'
                : trend === 'down'
                ? 'bg-rose-100 text-rose-700 border-rose-300 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800'
                : 'bg-slate-100 text-slate-700 border-slate-300 dark:bg-zinc-800 dark:text-zinc-300'
            }`}
          >
            {change}
          </span>
        )}
      </div>

      {description && <p className="text-xs text-slate-500 dark:text-zinc-400">{description}</p>}
    </GlassCard>
  )
}

// ── AI Result Card ───────────────────────────────────────────────────────────
export interface AIResultCardProps {
  score: number
  riskLevel: 'Low' | 'Medium' | 'High'
  estimatedRoi: number
  summary: string
  className?: string
}

export function AIResultCard({
  score,
  riskLevel,
  estimatedRoi,
  summary,
  className = '',
}: AIResultCardProps) {
  return (
    <GlassCard className={cn('p-6 sm:p-8 space-y-6 relative overflow-hidden', className)}>
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="space-y-1 text-center sm:text-left">
          <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            AI Startup Score
          </span>
          <h2 className="text-4xl sm:text-5xl font-black text-slate-900 dark:text-white">{score}%</h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400">High Success Probability</p>
        </div>

        <div className="grid grid-cols-2 gap-4 w-full sm:w-auto">
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 border border-slate-200/60 dark:border-zinc-700 text-center">
            <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-400 uppercase">Risk Level</span>
            <p className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">{riskLevel}</p>
          </div>
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 border border-slate-200/60 dark:border-zinc-700 text-center">
            <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-400 uppercase">Estimated ROI</span>
            <p className="text-lg font-extrabold text-cyan-600 dark:text-cyan-400 mt-0.5">{estimatedRoi}%</p>
          </div>
        </div>
      </div>

      <div className="p-4 rounded-2xl bg-cyan-50/60 dark:bg-cyan-950/30 border border-cyan-200/60 dark:border-cyan-800/40 text-xs text-cyan-900 dark:text-cyan-200 leading-relaxed">
        <span className="font-bold">AI Insight: </span> {summary}
      </div>
    </GlassCard>
  )
}
