/**
 * STARTWISE AI — Alert Banner Component
 */

import { useState, ReactNode } from 'react'
import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react'

export interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  children: ReactNode
  onClose?: () => void
  dismissible?: boolean
  className?: string
}

export function Alert({
  variant = 'info',
  title,
  children,
  onClose,
  dismissible = false,
  className = '',
}: AlertProps) {
  const [visible, setVisible] = useState(true)

  if (!visible) return null

  const variantStyles = {
    info: 'bg-cyan-50/80 dark:bg-cyan-950/40 border-cyan-200 dark:border-cyan-800/60 text-cyan-900 dark:text-cyan-200',
    success: 'bg-emerald-50/80 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/60 text-emerald-900 dark:text-emerald-200',
    warning: 'bg-amber-50/80 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/60 text-amber-900 dark:text-amber-200',
    error: 'bg-rose-50/80 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800/60 text-rose-900 dark:text-rose-200',
  }

  const icons = {
    info: <Info className="h-5 w-5 text-cyan-600 dark:text-cyan-400 flex-shrink-0" />,
    success: <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />,
    warning: <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0" />,
    error: <AlertCircle className="h-5 w-5 text-rose-600 dark:text-rose-400 flex-shrink-0" />,
  }

  const handleDismiss = () => {
    setVisible(false)
    if (onClose) onClose()
  }

  return (
    <div
      className={`p-4 rounded-2xl border backdrop-blur-md flex items-start gap-3 shadow-sm transition-all ${variantStyles[variant]} ${className}`}
    >
      {icons[variant]}
      <div className="flex-1 text-sm">
        {title && <h4 className="font-bold mb-1 leading-snug">{title}</h4>}
        <div className="leading-relaxed opacity-90">{children}</div>
      </div>
      {dismissible && (
        <button
          onClick={handleDismiss}
          className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 opacity-70 hover:opacity-100 transition-opacity"
          aria-label="Dismiss alert"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}
