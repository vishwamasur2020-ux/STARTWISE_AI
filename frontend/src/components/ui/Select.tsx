/**
 * STARTWISE AI — Select Input Component
 */

import { SelectHTMLAttributes, forwardRef, ReactNode } from 'react'

export interface SelectOption {
  label: string
  value: string | number
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: SelectOption[]
  error?: string
  leftIcon?: ReactNode
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, error, leftIcon, className = '', id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-semibold text-slate-700 dark:text-zinc-300">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3.5 pointer-events-none text-slate-400 dark:text-zinc-500">
              {leftIcon}
            </div>
          )}
          <select
            id={inputId}
            ref={ref}
            className={`w-full rounded-xl border bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white transition-all outline-none appearance-none cursor-pointer ${
              leftIcon ? 'pl-10' : 'pl-3.5'
            } ${
              error
                ? 'border-rose-500 focus:ring-2 focus:ring-rose-500/20'
                : 'border-slate-200/80 dark:border-zinc-700/80 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20'
            } ${className}`}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-white dark:bg-zinc-900 text-slate-900 dark:text-white">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        {error && <p className="text-xs font-medium text-rose-500 mt-1">{error}</p>}
      </div>
    )
  }
)

Select.displayName = 'Select'
