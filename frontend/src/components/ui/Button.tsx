/**
 * STARTWISE AI — Button Component
 * Polymorphic button with gradient, outline, ghost, and danger variants.
 */

import { forwardRef, ButtonHTMLAttributes } from 'react'
import { Loader2 } from 'lucide-react'
import { cn } from '@/utils/cn'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'gradient' | 'outline' | 'ghost' | 'danger' | 'secondary'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  fullWidth?: boolean
}

const variantClasses = {
  gradient:
    'btn-gradient disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:transform-none',
  outline:
    'btn-outline disabled:opacity-50 disabled:cursor-not-allowed',
  ghost:
    'btn-ghost disabled:opacity-50 disabled:cursor-not-allowed',
  danger:
    'inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold bg-red-500 text-white hover:bg-red-600 transition-all disabled:opacity-50',
  secondary:
    'inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold bg-slate-100 text-slate-800 hover:bg-slate-200 dark:bg-zinc-800 dark:text-slate-100 dark:hover:bg-zinc-700 transition-all disabled:opacity-50',
}

const sizeClasses = {
  sm: 'px-4 py-2 text-sm',
  md: 'px-6 py-3 text-sm',
  lg: 'px-8 py-4 text-base',
  xl: 'px-10 py-5 text-lg',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'gradient',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          variantClasses[variant],
          sizeClasses[size],
          fullWidth && 'w-full',
          className
        )}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          leftIcon
        )}
        {children}
        {!isLoading && rightIcon}
      </button>
    )
  }
)

Button.displayName = 'Button'
