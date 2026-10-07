/**
 * STARTWISE AI — Polished 6-Digit OTP Component
 * Features:
 * - 6 separate auto-advancing input cells
 * - Backspace backward navigation
 * - Full 6-digit paste handling
 * - Numeric-only filtering
 * - Error shake & highlighted borders
 * - Accessible ARIA labels & mobile keyboards
 * - Countdown timer & disabled cooldown resend button
 */

import { useState, useRef, useEffect, KeyboardEvent, ClipboardEvent, ChangeEvent } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { RefreshCw, AlertCircle } from 'lucide-react'

interface OTPInputProps {
  length?: number
  value: string
  onChange: (otp: string) => void
  onComplete?: (otp: string) => void
  error?: string | null
  disabled?: boolean
  autoFocus?: boolean
  cooldownSeconds?: number
  onResend?: () => void
  isResending?: boolean
  maskedEmail?: string
}

export function OTPInput({
  length = 6,
  value,
  onChange,
  onComplete,
  error,
  disabled = false,
  autoFocus = true,
  cooldownSeconds = 60,
  onResend,
  isResending = false,
  maskedEmail,
}: OTPInputProps) {
  const [digits, setDigits] = useState<string[]>(() => {
    const arr = value.split('').slice(0, length)
    while (arr.length < length) arr.push('')
    return arr
  })
  const [timeLeft, setTimeLeft] = useState(cooldownSeconds)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  // Keep internal digits in sync with value prop
  useEffect(() => {
    const arr = value.split('').slice(0, length)
    while (arr.length < length) arr.push('')
    setDigits(arr)
  }, [value, length])

  // Auto-focus first input on mount
  useEffect(() => {
    if (autoFocus && inputRefs.current[0]) {
      inputRefs.current[0].focus()
    }
  }, [autoFocus])

  // Countdown timer for resend cooldown
  useEffect(() => {
    if (timeLeft <= 0) return
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0))
    }, 1000)
    return () => clearInterval(timer)
  }, [timeLeft])

  const handleResendClick = () => {
    if (timeLeft > 0 || isResending || !onResend) return
    onResend()
    setTimeLeft(cooldownSeconds)
  }

  const handleChange = (index: number, e: ChangeEvent<HTMLInputElement>) => {
    const char = e.target.value.slice(-1)
    if (char && !/^\d$/.test(char)) return

    const newDigits = [...digits]
    newDigits[index] = char
    setDigits(newDigits)

    const fullVal = newDigits.join('')
    onChange(fullVal)

    if (char && index < length - 1) {
      inputRefs.current[index + 1]?.focus()
    }

    if (fullVal.length === length && !fullVal.includes('')) {
      onComplete?.(fullVal)
    }
  }

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace') {
      if (!digits[index] && index > 0) {
        inputRefs.current[index - 1]?.focus()
        const newDigits = [...digits]
        newDigits[index - 1] = ''
        setDigits(newDigits)
        onChange(newDigits.join(''))
      } else {
        const newDigits = [...digits]
        newDigits[index] = ''
        setDigits(newDigits)
        onChange(newDigits.join(''))
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus()
    } else if (e.key === 'ArrowRight' && index < length - 1) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').trim()
    const numericOnly = pasted.replace(/\D/g, '').slice(0, length)
    if (!numericOnly) return

    const newDigits = numericOnly.split('')
    while (newDigits.length < length) newDigits.push('')
    setDigits(newDigits)

    const fullVal = newDigits.join('')
    onChange(fullVal)

    // Focus last filled index or first empty
    const nextIdx = Math.min(numericOnly.length, length - 1)
    inputRefs.current[nextIdx]?.focus()

    if (numericOnly.length === length) {
      onComplete?.(numericOnly)
    }
  }

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      {maskedEmail && (
        <div className="text-center">
          <p className="text-xs uppercase font-bold tracking-wider text-cyan-600 dark:text-cyan-400 mb-1">
            Verification Code Sent
          </p>
          <p className="text-sm font-medium text-slate-700 dark:text-zinc-300">
            We've sent a 6-digit verification code to{' '}
            <span className="font-bold text-slate-900 dark:text-white underline decoration-cyan-500/40">
              {maskedEmail}
            </span>
          </p>
        </div>
      )}

      {/* 6-Digit Cells Grid */}
      <motion.div
        animate={error ? { x: [-8, 8, -6, 6, -3, 3, 0] } : {}}
        transition={{ duration: 0.4 }}
        className="flex items-center justify-center gap-2 sm:gap-3"
      >
        {Array.from({ length }).map((_, index) => {
          const isFilled = !!digits[index]
          const hasError = !!error

          return (
            <input
              key={index}
              ref={(el) => { inputRefs.current[index] = el }}
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={1}
              value={digits[index]}
              onChange={(e) => handleChange(index, e)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              onPaste={handlePaste}
              disabled={disabled}
              id={`otp-cell-${index}`}
              aria-label={`Digit ${index + 1} of verification code`}
              autoComplete="one-time-code"
              className={`
                w-11 h-14 sm:w-13 sm:h-16 text-center text-2xl font-black rounded-2xl
                transition-all duration-200 outline-none
                ${
                  hasError
                    ? 'border-2 border-rose-500 bg-rose-500/10 text-rose-600 dark:text-rose-400 focus:ring-4 focus:ring-rose-500/20'
                    : isFilled
                    ? 'border-2 border-cyan-500 bg-cyan-50/50 dark:bg-cyan-950/20 text-slate-900 dark:text-white shadow-md shadow-cyan-500/10'
                    : 'border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-slate-900 dark:text-white focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/20'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            />
          )
        })}
      </motion.div>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            className="flex items-center justify-center gap-1.5 text-xs font-semibold text-rose-600 dark:text-rose-400"
          >
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Timer & Resend Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 text-xs">
        <div className="flex items-center gap-2 text-slate-500 dark:text-zinc-400">
          <span className="inline-block h-2 w-2 rounded-full bg-cyan-500 animate-pulse" />
          <span>
            {timeLeft > 0 ? (
              <>
                Resend available in{' '}
                <span className="font-mono font-bold text-slate-800 dark:text-zinc-200">
                  {formatTimer(timeLeft)}
                </span>
              </>
            ) : (
              'Didn\'t receive code?'
            )}
          </span>
        </div>

        <button
          type="button"
          onClick={handleResendClick}
          disabled={timeLeft > 0 || isResending || disabled}
          className={`
            inline-flex items-center gap-1.5 font-bold transition-all
            ${
              timeLeft > 0 || isResending || disabled
                ? 'text-slate-400 dark:text-zinc-600 cursor-not-allowed'
                : 'text-cyan-600 dark:text-cyan-400 hover:text-cyan-700 dark:hover:text-cyan-300 hover:underline cursor-pointer'
            }
          `}
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isResending ? 'animate-spin' : ''}`} />
          {isResending ? 'Sending...' : 'Resend Code'}
        </button>
      </div>
    </div>
  )
}
