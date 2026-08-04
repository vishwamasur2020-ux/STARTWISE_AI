/**
 * STARTWISE AI — Textarea Component
 */

import { TextareaHTMLAttributes, forwardRef } from 'react'

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className = '', id, rows = 4, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-semibold text-slate-700 dark:text-zinc-300">
            {label}
          </label>
        )}
        <textarea
          id={inputId}
          ref={ref}
          rows={rows}
          className={`w-full rounded-xl border bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-zinc-500 transition-all outline-none resize-none ${
            error
              ? 'border-rose-500 focus:ring-2 focus:ring-rose-500/20'
              : 'border-slate-200/80 dark:border-zinc-700/80 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20'
          } ${className}`}
          {...props}
        />
        {error && <p className="text-xs font-medium text-rose-500 mt-1">{error}</p>}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'
