/**
 * STARTWISE AI — Reset Password Page
 * Accepts OTP/token, validates strong password requirements, and updates user credentials.
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { KeyRound, Lock, Eye, EyeOff, Sparkles, ArrowRight, ArrowLeft, CheckCircle2, XCircle } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/hooks/useAuth'

const resetPasswordSchema = z
  .object({
    otp_or_token: z.string().min(1, 'OTP or reset token is required'),
    new_password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Must contain an uppercase letter')
      .regex(/[a-z]/, 'Must contain a lowercase letter')
      .regex(/[0-9]/, 'Must contain a number'),
    confirm_password: z.string().min(1, 'Please confirm your new password'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

type ResetPasswordForm = z.infer<typeof resetPasswordSchema>

export default function ResetPasswordPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const { resetPassword, isSubmittingResetPassword } = useAuth()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ResetPasswordForm>({
    resolver: zodResolver(resetPasswordSchema),
  })

  const passwordValue = watch('new_password', '')

  const passwordChecks = [
    { label: 'At least 8 characters', valid: passwordValue.length >= 8 },
    { label: 'One uppercase letter (A-Z)', valid: /[A-Z]/.test(passwordValue) },
    { label: 'One lowercase letter (a-z)', valid: /[a-z]/.test(passwordValue) },
    { label: 'One number (0-9)', valid: /[0-9]/.test(passwordValue) },
  ]

  const onSubmit = (data: ResetPasswordForm) => {
    resetPassword({
      otp_or_token: data.otp_or_token,
      new_password: data.new_password,
      confirm_password: data.confirm_password,
    })
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

        <div className="mb-6">
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-2">
            Reset Password
          </h1>
          <p className="text-slate-500 dark:text-zinc-400 text-sm leading-relaxed">
            Enter your OTP or token received in email along with your new password.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <Input
            label="OTP or Reset Token"
            type="text"
            placeholder="Enter 6-digit OTP or token"
            leftIcon={<KeyRound className="h-4 w-4 text-slate-400" />}
            error={errors.otp_or_token?.message}
            required
            id="reset-otp"
            {...register('otp_or_token')}
          />

          <Input
            label="New Password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Enter new strong password"
            leftIcon={<Lock className="h-4 w-4 text-slate-400" />}
            rightIcon={
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="focus:outline-none text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                aria-label="Toggle new password visibility"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            }
            error={errors.new_password?.message}
            required
            id="reset-new-password"
            {...register('new_password')}
          />

          {/* Password Checks */}
          {passwordValue.length > 0 && (
            <div className="bg-slate-50 dark:bg-zinc-800/60 p-3 rounded-xl border border-slate-200/60 dark:border-zinc-700/50 space-y-1 text-xs">
              {passwordChecks.map((req, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  {req.valid ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                  ) : (
                    <XCircle className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
                  )}
                  <span className={req.valid ? 'text-emerald-600 dark:text-emerald-400 font-medium' : 'text-slate-500 dark:text-zinc-400'}>
                    {req.label}
                  </span>
                </div>
              ))}
            </div>
          )}

          <Input
            label="Confirm New Password"
            type={showConfirmPassword ? 'text' : 'password'}
            placeholder="Re-enter new password"
            leftIcon={<Lock className="h-4 w-4 text-slate-400" />}
            rightIcon={
              <button
                type="button"
                onClick={() => setShowConfirmPassword((v) => !v)}
                className="focus:outline-none text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                aria-label="Toggle confirm password visibility"
              >
                {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            }
            error={errors.confirm_password?.message}
            required
            id="reset-confirm-password"
            {...register('confirm_password')}
          />

          <Button
            type="submit"
            fullWidth
            size="lg"
            isLoading={isSubmittingResetPassword}
            rightIcon={<ArrowRight className="h-4 w-4" />}
            className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg shadow-cyan-500/25 mt-2"
          >
            {isSubmittingResetPassword ? 'Resetting...' : 'Update Password'}
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
      </motion.div>
    </div>
  )
}
