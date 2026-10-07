/**
 * STARTWISE AI — Password Strength Indicator Component
 * Evaluates strength: Weak, Fair, Good, Strong.
 * Displays animated colored strength meter bar and security checks.
 */

import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2, XCircle } from 'lucide-react'

interface PasswordStrengthIndicatorProps {
  password: string
  showCriteria?: boolean
}

export function PasswordStrengthIndicator({
  password,
  showCriteria = true,
}: PasswordStrengthIndicatorProps) {
  const { label, colorClass, widthPercent, checks } = useMemo(() => {
    const checksList = [
      { label: '8+ characters', valid: password.length >= 8 },
      { label: 'Uppercase letter (A-Z)', valid: /[A-Z]/.test(password) },
      { label: 'Lowercase letter (a-z)', valid: /[a-z]/.test(password) },
      { label: 'Digit (0-9)', valid: /[0-9]/.test(password) },
      { label: 'Special character (!@#$...)', valid: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password) },
    ]

    const passedCount = checksList.filter((c) => c.valid).length

    if (!password) {
      return { score: 0, label: '', colorClass: '', widthPercent: 0, checks: checksList }
    }

    if (passedCount <= 2 || password.length < 8) {
      return {
        score: 1,
        label: 'Weak',
        colorClass: 'bg-rose-500 text-rose-500',
        widthPercent: 25,
        checks: checksList,
      }
    } else if (passedCount === 3) {
      return {
        score: 2,
        label: 'Fair',
        colorClass: 'bg-amber-500 text-amber-500',
        widthPercent: 50,
        checks: checksList,
      }
    } else if (passedCount === 4) {
      return {
        score: 3,
        label: 'Good',
        colorClass: 'bg-blue-500 text-blue-500',
        widthPercent: 75,
        checks: checksList,
      }
    } else {
      return {
        score: 4,
        label: 'Strong',
        colorClass: 'bg-emerald-500 text-emerald-500',
        widthPercent: 100,
        checks: checksList,
      }
    }
  }, [password])

  if (!password) return null

  return (
    <div className="space-y-2 mt-2">
      {/* Strength Bar & Label */}
      <div className="flex items-center justify-between text-xs font-semibold">
        <span className="text-slate-500 dark:text-zinc-400">Password Strength:</span>
        <span className={`font-bold ${colorClass.split(' ')[1]}`}>{label}</span>
      </div>

      <div className="h-1.5 w-full bg-slate-200 dark:bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${colorClass.split(' ')[0]} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${widthPercent}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>

      {/* Criteria Breakdown */}
      {showCriteria && (
        <div className="grid grid-cols-2 gap-1.5 pt-1 text-[11px]">
          {checks.map((req, idx) => (
            <div key={idx} className="flex items-center gap-1.5">
              {req.valid ? (
                <CheckCircle2 className="h-3 w-3 text-emerald-500 flex-shrink-0" />
              ) : (
                <XCircle className="h-3 w-3 text-slate-400 flex-shrink-0" />
              )}
              <span
                className={
                  req.valid
                    ? 'text-emerald-600 dark:text-emerald-400 font-medium'
                    : 'text-slate-500 dark:text-zinc-400'
                }
              >
                {req.label}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
