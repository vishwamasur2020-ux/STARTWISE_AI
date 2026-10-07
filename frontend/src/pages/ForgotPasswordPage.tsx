/**
 * STARTWISE AI — Forgot Password Page
 * Allows users to request a 6-digit password reset OTP via email.
 * Implements strict email-enumeration prevention.
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Mail, ArrowLeft, ArrowRight, Sparkles, CheckCircle, ShieldCheck } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/hooks/useAuth'

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
})

type ForgotPasswordForm = z.infer<typeof forgotPasswordSchema>

export default function ForgotPasswordPage() {
  const [submittedEmail, setSubmittedEmail] = useState<string | null>(null)
  const { forgotPasswordAsync, isSubmittingForgotPassword } = useAuth()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordForm>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  const onSubmit = async (data: ForgotPasswordForm) => {
    try {
      await forgotPasswordAsync({ email: data.email.trim() })
      setSubmittedEmail(data.email.trim())
    } catch {
      // Even on non-200, still show generic safe response
      setSubmittedEmail(data.email.trim())
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center animated-bg p-4 sm:p-6 text-slate-900 dark:text-white">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 16 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md glass-card p-6 sm:p-10 rounded-3xl shadow-xl border border-slate-200/60 dark:border-white/10 bg-white/85 dark:bg-zinc-900/85 backdrop-blur-xl"
      >
        <Link to="/" className="flex items-center gap-2 mb-8 group w-fit">
          <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white shadow group-hover:scale-105 transition-transform">
            <Sparkles className="h-4 w-4" />
          </div>
          <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">STARTWISE AI</span>
        </Link>

        {submittedEmail ? (
          <div className="text-center py-4 space-y-4">
            <div className="h-16 w-16 rounded-2xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto shadow-sm">
              <CheckCircle className="h-8 w-8" />
            </div>
            <h2 className="text-2xl font-black text-slate-900 dark:text-white">Verification Code Sent</h2>
            <p className="text-slate-600 dark:text-zinc-400 text-sm leading-relaxed">
              If an account exists for <span className="font-bold text-slate-900 dark:text-white">{submittedEmail}</span>, a 6-digit verification code has been sent.
            </p>
            <p className="text-xs text-slate-400 dark:text-zinc-500">
              The code will expire in 10 minutes.
            </p>

            <div className="space-y-3 pt-2">
              <Button
                onClick={() => navigate('/reset-password', { state: { email: submittedEmail } })}
                fullWidth
                size="lg"
                rightIcon={<ArrowRight className="h-4 w-4" />}
                className="bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-xl shadow-lg"
              >
                Enter OTP & Reset Password
              </Button>

              <button
                type="button"
                onClick={() => setSubmittedEmail(null)}
                className="text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline block mx-auto pt-1"
              >
                Didn't receive email? Try another address
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="mb-6 space-y-2">
              <div className="h-12 w-12 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shadow-sm">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                Forgot Password?
              </h1>
              <p className="text-slate-500 dark:text-zinc-400 text-sm leading-relaxed">
                Enter your registered email address to receive a secure 6-digit password reset OTP.
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
              <Input
                label="Registered Email"
                type="email"
                placeholder="you@example.com"
                leftIcon={<Mail className="h-4 w-4 text-slate-400" />}
                error={errors.email?.message}
                required
                id="forgot-password-email"
                {...register('email')}
              />

              <Button
                type="submit"
                fullWidth
                size="lg"
                isLoading={isSubmittingForgotPassword}
                rightIcon={<ArrowRight className="h-4 w-4" />}
                className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-cyan-500/25"
              >
                {isSubmittingForgotPassword ? 'Sending...' : 'Send OTP'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <Link
                to="/login"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white transition-colors"
              >
                <ArrowLeft className="h-3.5 w-3.5" /> Back to Sign In
              </Link>
            </div>
          </>
        )}
      </motion.div>
    </div>
  )
}
