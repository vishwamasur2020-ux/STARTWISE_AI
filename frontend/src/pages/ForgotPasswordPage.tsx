/**
 * STARTWISE AI — Forgot Password Page
 * Allows users to request a password reset link/OTP via email.
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Mail, ArrowLeft, ArrowRight, Sparkles, CheckCircle } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/hooks/useAuth'

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
})

type ForgotPasswordForm = z.infer<typeof forgotPasswordSchema>

export default function ForgotPasswordPage() {
  const [submittedEmail, setSubmittedEmail] = useState<string | null>(null)
  const { forgotPassword, isSubmittingForgotPassword } = useAuth()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordForm>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  const onSubmit = (data: ForgotPasswordForm) => {
    forgotPassword(
      { email: data.email },
      {
        onSuccess: () => setSubmittedEmail(data.email),
      }
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center animated-bg p-6 text-slate-900 dark:text-white">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 16 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md glass-card p-8 sm:p-10 rounded-3xl shadow-xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl"
      >
        <Link to="/" className="flex items-center gap-2 mb-8 group w-fit">
          <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white shadow group-hover:scale-105 transition-transform">
            <Sparkles className="h-4 w-4" />
          </div>
          <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">STARTWISE AI</span>
        </Link>

        {submittedEmail ? (
          <div className="text-center py-4">
            <div className="h-16 w-16 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto mb-5">
              <CheckCircle className="h-8 w-8" />
            </div>
            <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white mb-2">Check your email</h2>
            <p className="text-slate-600 dark:text-zinc-400 text-sm leading-relaxed mb-6">
              We sent a password reset OTP/link to <span className="font-semibold text-slate-900 dark:text-white">{submittedEmail}</span>.
            </p>

            <div className="space-y-3">
              <Button
                onClick={() => navigate('/reset-password')}
                fullWidth
                size="lg"
                rightIcon={<ArrowRight className="h-4 w-4" />}
                className="bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-semibold rounded-xl"
              >
                Enter OTP / Reset Password
              </Button>

              <button
                type="button"
                onClick={() => setSubmittedEmail(null)}
                className="text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline block mx-auto pt-2"
              >
                Didn't get the email? Try again
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="mb-6">
              <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-2">
                Forgot password?
              </h1>
              <p className="text-slate-500 dark:text-zinc-400 text-sm leading-relaxed">
                No worries! Enter your email address below and we'll send you a password reset token/OTP.
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
              <Input
                label="Email Address"
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
                className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg shadow-cyan-500/25"
              >
                {isSubmittingForgotPassword ? 'Sending...' : 'Send Reset Link'}
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
