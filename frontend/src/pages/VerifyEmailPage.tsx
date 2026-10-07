/**
 * STARTWISE AI — Verify Email Page
 * Complete 6-digit OTP email verification with masked email display,
 * 60-second resend cooldown timer, error handling, and animated success confirmation.
 */

import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Mail, CheckCircle2, ArrowRight, ArrowLeft, Sparkles, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { OTPInput } from '@/components/auth/OTPInput'
import { useAuth } from '@/hooks/useAuth'

// Mask email e.g. contact@gmail.com -> c****t@gmail.com
function maskEmail(email: string): string {
  if (!email || !email.includes('@')) return email || ''
  const [local, domain] = email.split('@')
  if (local.length <= 2) {
    return `${local[0]}*@${domain}`
  }
  const first = local[0]
  const last = local[local.length - 1]
  const stars = '*'.repeat(Math.max(local.length - 2, 4))
  return `${first}${stars}${last}@${domain}`
}

export default function VerifyEmailPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { verifyEmailAsync, resendOTPAsync, isVerifyingEmail, isResendingOTP } = useAuth()

  // Grab initial email from router state or query param
  const initialEmail = (location.state as any)?.email || ''
  const [email, setEmail] = useState<string>(initialEmail)
  const [isEditingEmail, setIsEditingEmail] = useState<boolean>(!initialEmail)
  const [otp, setOtp] = useState<string>('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isVerifiedSuccess, setIsVerifiedSuccess] = useState<boolean>(false)

  const handleVerify = async (codeToVerify?: string) => {
    const code = codeToVerify || otp
    setErrorMessage(null)

    if (!email) {
      setErrorMessage('Please enter your email address.')
      setIsEditingEmail(true)
      return
    }

    if (!code || code.length !== 6) {
      setErrorMessage('Please enter all 6 digits of your verification code.')
      return
    }

    try {
      const response = await verifyEmailAsync({
        email: email.trim(),
        otp: code.trim(),
      })

      setIsVerifiedSuccess(true)
      toast.success(response.message || 'Email verified successfully! 🎉')
      setTimeout(() => {
        navigate('/login', { state: { email } })
      }, 2000)
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setErrorMessage(detail)
      } else {
        setErrorMessage('Verification failed. Please check the code and try again.')
      }
    }
  }

  const handleResend = async () => {
    setErrorMessage(null)
    if (!email) {
      setErrorMessage('Please enter your email address to resend the code.')
      setIsEditingEmail(true)
      return
    }

    try {
      await resendOTPAsync({
        email: email.trim(),
        purpose: 'EMAIL_VERIFICATION',
      })
      toast.success('A new verification code has been sent! ✉️')
      setOtp('')
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setErrorMessage(detail)
      } else {
        setErrorMessage('Unable to resend verification code. Please wait before trying again.')
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center animated-bg p-4 sm:p-6 text-slate-900 dark:text-white">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 16 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-lg glass-card p-6 sm:p-10 rounded-3xl shadow-2xl border border-slate-200/60 dark:border-white/10 bg-white/85 dark:bg-zinc-900/85 backdrop-blur-2xl"
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between mb-8">
          <Link to="/" className="flex items-center gap-2 group w-fit">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white shadow group-hover:scale-105 transition-transform">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">
              STARTWISE AI
            </span>
          </Link>

          <Link
            to="/login"
            className="text-xs font-semibold text-slate-500 dark:text-zinc-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors inline-flex items-center gap-1"
          >
            <ArrowLeft className="h-3 w-3" /> Back to Login
          </Link>
        </div>

        {isVerifiedSuccess ? (
          /* ── Success Celebration State ────────────────────────────────────────── */
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-6 space-y-4"
          >
            <div className="h-20 w-20 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto shadow-inner ring-8 ring-emerald-500/10">
              <CheckCircle2 className="h-10 w-10 animate-bounce" />
            </div>
            <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              ✓ Email Verified Successfully
            </h2>
            <p className="text-slate-600 dark:text-zinc-400 text-sm max-w-sm mx-auto leading-relaxed">
              Your STARTWISE AI account is now verified and fully activated. Redirecting you to login...
            </p>
            <div className="pt-2">
              <Button
                onClick={() => navigate('/login', { state: { email } })}
                fullWidth
                rightIcon={<ArrowRight className="h-4 w-4" />}
                className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold rounded-xl shadow-lg"
              >
                Continue to Login
              </Button>
            </div>
          </motion.div>
        ) : (
          /* ── Verification Form ─────────────────────────────────────────────────── */
          <div className="space-y-6">
            <div className="text-center space-y-2">
              <div className="h-14 w-14 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mx-auto shadow-sm">
                <ShieldCheck className="h-7 w-7" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                Verify Your Email
              </h1>
              <p className="text-slate-500 dark:text-zinc-400 text-sm">
                Enter the 6-digit confirmation code we sent to your inbox.
              </p>
            </div>

            {/* Email Banner / Edit Switch */}
            {isEditingEmail ? (
              <div className="space-y-2 bg-slate-50 dark:bg-zinc-800/60 p-4 rounded-2xl border border-slate-200 dark:border-white/5">
                <Input
                  label="Registered Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  leftIcon={<Mail className="h-4 w-4 text-slate-400" />}
                  id="verify-email-input"
                  required
                />
                {email && (
                  <button
                    type="button"
                    onClick={() => setIsEditingEmail(false)}
                    className="text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline pt-1 block"
                  >
                    Confirm Email & Continue
                  </button>
                )}
              </div>
            ) : (
              <div className="bg-slate-100/80 dark:bg-zinc-800/50 px-4 py-3 rounded-2xl flex items-center justify-between border border-slate-200/60 dark:border-white/5">
                <div className="flex items-center gap-2.5 min-w-0">
                  <Mail className="h-4 w-4 text-cyan-600 dark:text-cyan-400 flex-shrink-0" />
                  <span className="text-xs font-bold text-slate-700 dark:text-zinc-300 truncate font-mono">
                    {maskEmail(email)}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setIsEditingEmail(true)}
                  className="text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:underline ml-2 flex-shrink-0"
                >
                  Change
                </button>
              </div>
            )}

            {/* OTP Input Component */}
            <div className="pt-2">
              <OTPInput
                length={6}
                value={otp}
                onChange={(val) => {
                  setOtp(val)
                  if (errorMessage) setErrorMessage(null)
                }}
                onComplete={(val) => handleVerify(val)}
                error={errorMessage}
                disabled={isVerifyingEmail || isResendingOTP}
                cooldownSeconds={60}
                onResend={handleResend}
                isResending={isResendingOTP}
              />
            </div>

            {/* Primary Action Button */}
            <Button
              type="button"
              onClick={() => handleVerify()}
              isLoading={isVerifyingEmail}
              disabled={otp.length !== 6 || isVerifyingEmail}
              fullWidth
              size="lg"
              rightIcon={<ArrowRight className="h-4 w-4" />}
              className="bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-cyan-500/20"
            >
              Verify Email
            </Button>

            <div className="text-center pt-2">
              <p className="text-xs text-slate-500 dark:text-zinc-500">
                Code expires in 10 minutes • Check spam folder if not received
              </p>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
