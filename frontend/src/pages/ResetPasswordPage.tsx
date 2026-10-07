/**
 * STARTWISE AI — Reset Password Page
 * Accepts 6-digit OTP, new password, confirmation, and updates credentials.
 * Includes interactive PasswordStrengthIndicator and 60-second OTP resend cooldown.
 */

import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Lock, Mail, Eye, EyeOff, Sparkles, ArrowRight, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { OTPInput } from '@/components/auth/OTPInput'
import { PasswordStrengthIndicator } from '@/components/auth/PasswordStrengthIndicator'
import { useAuth } from '@/hooks/useAuth'

const resetPasswordSchema = z
  .object({
    email: z.string().email('Please enter a valid email address'),
    new_password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Must contain an uppercase letter')
      .regex(/[a-z]/, 'Must contain a lowercase letter')
      .regex(/[0-9]/, 'Must contain a number')
      .regex(/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/, 'Must contain a special character'),
    confirm_password: z.string().min(1, 'Please confirm your new password'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

type ResetPasswordForm = z.infer<typeof resetPasswordSchema>

export default function ResetPasswordPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const initialEmail = (location.state as any)?.email || ''

  const [email, setEmail] = useState<string>(initialEmail)
  const [otp, setOtp] = useState<string>('')
  const [otpError, setOtpError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const { resetPasswordAsync, resendOTPAsync, isSubmittingResetPassword, isResendingOTP } = useAuth()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ResetPasswordForm>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      email: initialEmail,
      new_password: '',
      confirm_password: '',
    },
  })

  const newPasswordValue = watch('new_password', '')

  const handleResendOTP = async () => {
    setOtpError(null)
    if (!email) {
      setOtpError('Please provide your email address above to resend the code.')
      return
    }

    try {
      await resendOTPAsync({
        email: email.trim(),
        purpose: 'PASSWORD_RESET',
      })
      toast.success('Password reset OTP sent! ✉️')
      setOtp('')
    } catch (err: any) {
      const detail = err.response?.data?.detail
      setOtpError(typeof detail === 'string' ? detail : 'Unable to resend OTP. Please wait a moment.')
    }
  }

  const onSubmit = async (data: ResetPasswordForm) => {
    setOtpError(null)
    if (!otp || otp.length !== 6) {
      setOtpError('Please enter the 6-digit verification code.')
      return
    }

    try {
      const res = await resetPasswordAsync({
        email: data.email.trim(),
        otp: otp.trim(),
        new_password: data.new_password,
      })

      toast.success(res.message || 'Password reset successfully.')
      setTimeout(() => {
        navigate('/login', { state: { email: data.email } })
      }, 1500)
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        if (detail.toLowerCase().includes('otp') || detail.toLowerCase().includes('attempt')) {
          setOtpError(detail)
        } else {
          toast.error(detail)
        }
      } else {
        toast.error('Failed to reset password. Please check your OTP and try again.')
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center animated-bg p-4 sm:p-6 text-slate-900 dark:text-white">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 16 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-lg glass-card p-6 sm:p-10 rounded-3xl shadow-xl border border-slate-200/60 dark:border-white/10 bg-white/85 dark:bg-zinc-900/85 backdrop-blur-xl"
      >
        <div className="flex items-center justify-between mb-8">
          <Link to="/" className="flex items-center gap-2 group w-fit">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white shadow group-hover:scale-105 transition-transform">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">STARTWISE AI</span>
          </Link>

          <Link
            to="/login"
            className="text-xs font-semibold text-slate-500 dark:text-zinc-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors inline-flex items-center gap-1"
          >
            <ArrowLeft className="h-3 w-3" /> Back to Login
          </Link>
        </div>

        <div className="mb-6 space-y-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Reset Password
          </h1>
          <p className="text-slate-500 dark:text-zinc-400 text-sm">
            Enter the 6-digit OTP sent to your email along with your new password.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
          {/* Email input */}
          <Input
            label="Email Address"
            type="email"
            placeholder="you@example.com"
            leftIcon={<Mail className="h-4 w-4 text-slate-400" />}
            error={errors.email?.message}
            required
            id="reset-email"
            {...register('email', {
              onChange: (e) => setEmail(e.target.value),
            })}
          />

          {/* 6-Digit OTP */}
          <div className="space-y-1 pt-1">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-zinc-300">
              6-Digit Verification Code
            </label>
            <OTPInput
              length={6}
              value={otp}
              onChange={(val) => {
                setOtp(val)
                if (otpError) setOtpError(null)
              }}
              error={otpError}
              disabled={isSubmittingResetPassword || isResendingOTP}
              cooldownSeconds={60}
              onResend={handleResendOTP}
              isResending={isResendingOTP}
            />
          </div>

          {/* New Password */}
          <div>
            <div className="relative">
              <Input
                label="New Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                leftIcon={<Lock className="h-4 w-4 text-slate-400" />}
                rightIcon={
                  <button
                    type="button"
                    tabIndex={-1}
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                }
                error={errors.new_password?.message}
                required
                id="reset-new-password"
                {...register('new_password')}
              />
            </div>

            {/* Password strength meter */}
            {newPasswordValue && (
              <div className="mt-2.5">
                <PasswordStrengthIndicator password={newPasswordValue} showCriteria={true} />
              </div>
            )}
          </div>

          {/* Confirm New Password */}
          <Input
            label="Confirm New Password"
            type={showConfirmPassword ? 'text' : 'password'}
            placeholder="••••••••"
            leftIcon={<Lock className="h-4 w-4 text-slate-400" />}
            rightIcon={
              <button
                type="button"
                tabIndex={-1}
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
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
            disabled={isSubmittingResetPassword || otp.length !== 6}
            rightIcon={<ArrowRight className="h-4 w-4" />}
            className="bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-cyan-500/25 mt-4"
          >
            {isSubmittingResetPassword ? 'Resetting Password...' : 'Reset Password'}
          </Button>
        </form>
      </motion.div>
    </div>
  )
}
