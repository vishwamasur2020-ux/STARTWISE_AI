/**
 * STARTWISE AI — Security Settings Page (/settings/security)
 * Allows authenticated users to change their password with current password verification,
 * strength checks, session security details, and verification status.
 */

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { ShieldCheck, Lock, Eye, EyeOff, KeyRound, CheckCircle2, ShieldAlert, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { PasswordStrengthIndicator } from '@/components/auth/PasswordStrengthIndicator'
import { useAuth } from '@/hooks/useAuth'

const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, 'Current password is required'),
    new_password: z
      .string()
      .min(8, 'New password must be at least 8 characters')
      .regex(/[A-Z]/, 'Must contain an uppercase letter')
      .regex(/[a-z]/, 'Must contain a lowercase letter')
      .regex(/[0-9]/, 'Must contain a number')
      .regex(/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/, 'Must contain a special character'),
    confirm_password: z.string().min(1, 'Please confirm your new password'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'New passwords do not match',
    path: ['confirm_password'],
  })
  .refine((data) => data.current_password !== data.new_password, {
    message: 'New password cannot be the same as the current password',
    path: ['new_password'],
  })

type ChangePasswordForm = z.infer<typeof changePasswordSchema>

export default function SecuritySettingsPage() {
  const { user, changePasswordAsync, isChangingPassword } = useAuth()
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordForm>({
    resolver: zodResolver(changePasswordSchema),
  })

  const newPasswordValue = watch('new_password', '')

  const onSubmit = async (data: ChangePasswordForm) => {
    try {
      const res = await changePasswordAsync({
        current_password: data.current_password,
        new_password: data.new_password,
      })
      toast.success(res.message || 'Password changed successfully! 🔐')
      reset()
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        toast.error(detail)
      } else {
        toast.error('Failed to change password. Please check your current password.')
      }
    }
  }

  const isVerified = user?.email_verified ?? user?.is_verified ?? false

  return (
    <div className="max-w-4xl mx-auto space-y-8 p-4 sm:p-8">
      {/* ── Breadcrumb & Header ─────────────────────────────────────────────── */}
      <div className="space-y-2">
        <Link
          to="/profile"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 dark:text-zinc-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Profile & Settings
        </Link>
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white shadow-md">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
              Security Settings
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-zinc-400">
              Manage your credentials, password updates, and account verification status.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* ── Change Password Form ───────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 glass-card p-6 sm:p-8 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl space-y-6"
        >
          <div className="flex items-center gap-2 border-b border-slate-100 dark:border-white/5 pb-4">
            <KeyRound className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Change Password</h2>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
            {/* Current Password */}
            <Input
              label="Current Password"
              type={showCurrentPassword ? 'text' : 'password'}
              placeholder="••••••••"
              leftIcon={<Lock className="h-4 w-4 text-slate-400" />}
              rightIcon={
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  {showCurrentPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
              error={errors.current_password?.message}
              required
              id="change-current-password"
              {...register('current_password')}
            />

            {/* New Password */}
            <div>
              <Input
                label="New Password"
                type={showNewPassword ? 'text' : 'password'}
                placeholder="••••••••"
                leftIcon={<Lock className="h-4 w-4 text-slate-400" />}
                rightIcon={
                  <button
                    type="button"
                    tabIndex={-1}
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                }
                error={errors.new_password?.message}
                required
                id="change-new-password"
                {...register('new_password')}
              />

              {newPasswordValue && (
                <div className="mt-3">
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
              id="change-confirm-password"
              {...register('confirm_password')}
            />

            <div className="pt-2 flex justify-end">
              <Button
                type="submit"
                isLoading={isChangingPassword}
                disabled={isChangingPassword}
                className="bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-xl px-6 shadow-md"
              >
                Change Password
              </Button>
            </div>
          </form>
        </motion.div>

        {/* ── Security Sidebar ────────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-6"
        >
          {/* Account Verification Card */}
          <div className="glass-card p-6 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
              Verification Status
            </h3>

            <div className="flex items-center gap-3">
              <div
                className={`h-10 w-10 rounded-xl flex items-center justify-center ${
                  isVerified
                    ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400'
                    : 'bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400'
                }`}
              >
                {isVerified ? <CheckCircle2 className="h-5 w-5" /> : <ShieldAlert className="h-5 w-5" />}
              </div>
              <div>
                <p className="font-bold text-sm text-slate-900 dark:text-white">
                  {isVerified ? 'Email Verified' : 'Email Unverified'}
                </p>
                <p className="text-xs text-slate-500 dark:text-zinc-400 font-mono truncate max-w-[180px]">
                  {user?.email}
                </p>
              </div>
            </div>

            {!isVerified && (
              <Link
                to="/verify-email"
                state={{ email: user?.email }}
                className="block text-center w-full py-2 px-3 rounded-xl bg-amber-500 text-white font-bold text-xs hover:bg-amber-600 transition-colors shadow-sm"
              >
                Verify Email Now →
              </Link>
            )}
          </div>

          {/* Session Information */}
          <div className="glass-card p-6 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl space-y-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
              Session Protection
            </h3>
            <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
              Your session is secured using encrypted JWT tokens. Changing your password updates database credentials and immediately logs out unauthorized sessions.
            </p>
            <div className="p-3 bg-slate-50 dark:bg-zinc-800/60 rounded-xl border border-slate-100 dark:border-white/5 text-[11px] text-slate-500 dark:text-zinc-400 space-y-1">
              <div className="flex justify-between">
                <span>Account Role:</span>
                <span className="font-bold uppercase text-slate-900 dark:text-white">{user?.role}</span>
              </div>
              <div className="flex justify-between">
                <span>Security Protocol:</span>
                <span className="font-bold text-emerald-600 dark:text-emerald-400">HMAC-SHA256</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
