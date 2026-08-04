/**
 * STARTWISE AI — Radio Input Component
 */

import { InputHTMLAttributes, forwardRef } from 'react'

export interface RadioOption {
  label: string
  value: string
  description?: string
}

export interface RadioGroupProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  label?: string
  options: RadioOption[]
  name: string
  value?: string
  onChange?: (value: string) => void
  error?: string
}

export const RadioGroup = forwardRef<HTMLInputElement, RadioGroupProps>(
  ({ label, options, name, value, onChange, error, className = '', ...props }, ref) => {
    return (
      <div className="w-full space-y-2">
        {label && (
          <label className="block text-xs font-semibold text-slate-700 dark:text-zinc-300 mb-1">
            {label}
          </label>
        )}
        <div className={`space-y-2 ${className}`}>
          {options.map((opt) => {
            const isChecked = value === opt.value
            return (
              <label
                key={opt.value}
                className={`flex items-start gap-3 p-3.5 rounded-2xl border transition-all cursor-pointer ${
                  isChecked
                    ? 'bg-cyan-50/80 dark:bg-cyan-950/40 border-cyan-500 ring-1 ring-cyan-500/20'
                    : 'bg-white/60 dark:bg-zinc-900/60 border-slate-200/80 dark:border-zinc-800 hover:border-slate-300'
                }`}
              >
                <input
                  type="radio"
                  ref={ref}
                  name={name}
                  value={opt.value}
                  checked={isChecked}
                  onChange={() => onChange && onChange(opt.value)}
                  className="mt-0.5 h-4 w-4 text-cyan-600 focus:ring-cyan-500 border-slate-300 dark:border-zinc-700"
                  {...props}
                />
                <div className="text-xs">
                  <span className="font-bold text-slate-900 dark:text-white block">{opt.label}</span>
                  {opt.description && (
                    <span className="text-slate-500 dark:text-zinc-400 mt-0.5 block leading-relaxed">
                      {opt.description}
                    </span>
                  )}
                </div>
              </label>
            )
          })}
        </div>
        {error && <p className="text-xs font-medium text-rose-500 mt-1">{error}</p>}
      </div>
    )
  }
)

RadioGroup.displayName = 'RadioGroup'
