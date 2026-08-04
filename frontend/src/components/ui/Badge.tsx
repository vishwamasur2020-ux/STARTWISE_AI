/**
 * STARTWISE AI — Badge Component
 */

import { HTMLAttributes } from 'react'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'glass'
  size?: 'sm' | 'md'
}

export function Badge({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  ...props
}: BadgeProps) {
  const variantStyles = {
    primary: 'bg-cyan-100 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 border-cyan-300 dark:border-cyan-700',
    secondary: 'bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-700',
    success: 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700',
    warning: 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-700',
    danger: 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border-rose-300 dark:border-rose-700',
    glass: 'bg-white/20 dark:bg-black/20 text-slate-800 dark:text-white border-white/30 backdrop-blur-md',
  }

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider',
    md: 'px-2.5 py-1 text-xs font-semibold uppercase tracking-wide',
  }

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border shadow-sm ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {children}
    </span>
  )
}
