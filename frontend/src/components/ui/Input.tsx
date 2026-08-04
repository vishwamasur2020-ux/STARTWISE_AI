/**
 * STARTWISE AI — Input Component
 * Premium input with label, error state, icon support, and helper text.
 */

import { forwardRef, InputHTMLAttributes } from 'react'
import { AlertCircle } from 'lucide-react'
import { cn } from '@/utils/cn'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  fullWidth?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { label, error, helperText, leftIcon, rightIcon, fullWidth = true, className, id, ...props },
    ref
  ) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className={cn('flex flex-col gap-1.5', fullWidth && 'w-full')}>
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-semibold text-slate-700 dark:text-slate-300"
          >
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'input-premium',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-red-400 focus:ring-red-400/40 focus:border-red-400',
              className
            )}
            {...props}
          />
          {rightIcon && !error && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
              {rightIcon}
            </div>
          )}
          {error && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-red-500">
              <AlertCircle className="h-4 w-4" />
            </div>
          )}
        </div>

        {error && (
          <p className="text-xs text-red-500 flex items-center gap-1 mt-0.5">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="text-xs text-slate-400 dark:text-zinc-500">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
