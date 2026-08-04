/**
 * STARTWISE AI — Checkbox Input Component
 */

import { InputHTMLAttributes, forwardRef, ReactNode } from 'react'

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: ReactNode
  error?: string
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, error, className = '', id, ...props }, ref) => {
    const inputId = id || (typeof label === 'string' ? label.toLowerCase().replace(/\s+/g, '-') : undefined)

    return (
      <div className="space-y-1">
        <label htmlFor={inputId} className="inline-flex items-center gap-2.5 cursor-pointer select-none">
          <input
            id={inputId}
            type="checkbox"
            ref={ref}
            className={`h-4 w-4 rounded border-slate-300 dark:border-zinc-700 text-cyan-600 focus:ring-cyan-500/20 focus:ring-2 transition-all cursor-pointer ${className}`}
            {...props}
          />
          {label && <span className="text-xs font-semibold text-slate-700 dark:text-zinc-300">{label}</span>}
        </label>
        {error && <p className="text-xs font-medium text-rose-500 mt-0.5">{error}</p>}
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'
