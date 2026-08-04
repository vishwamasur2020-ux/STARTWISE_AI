/**
 * STARTWISE AI — Profile Page
 * User profile management, avatar update, location/phone updates, role badge, and security settings.
 */

import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { User as UserIcon, Mail, Phone, MapPin, ShieldCheck, Camera, LogOut, KeyRound, Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/hooks/useAuth'

const profileSchema = z.object({
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  phone_number: z.string().optional(),
  location: z.string().optional(),
  profile_image: z.string().optional(),
})

type ProfileForm = z.infer<typeof profileSchema>

export default function ProfilePage() {
  const { user, updateProfile, isUpdatingProfile, logout } = useAuth()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user?.full_name || '',
      phone_number: user?.phone_number || user?.phone || '',
      location: user?.location || '',
      profile_image: user?.profile_image || user?.avatar_url || '',
    },
  })

  useEffect(() => {
    if (user) {
      reset({
        full_name: user.full_name,
        phone_number: user.phone_number || user.phone || '',
        location: user.location || '',
        profile_image: user.profile_image || user.avatar_url || '',
      })
    }
  }, [user, reset])

  const onSubmit = (data: ProfileForm) => {
    updateProfile({
      full_name: data.full_name,
      phone_number: data.phone_number,
      location: data.location,
      profile_image: data.profile_image,
    })
  }

  const avatarUrl =
    user?.profile_image || user?.avatar_url || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(user?.full_name || 'User')}`

  return (
    <div className="max-w-4xl mx-auto space-y-8 p-4 sm:p-8">
      {/* ── Profile Header Glass Banner ──────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-cyan-400/20 to-indigo-500/0 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 relative z-10">
          <div className="relative group">
            <img
              src={avatarUrl}
              alt={user?.full_name}
              className="h-24 w-24 rounded-2xl object-cover ring-4 ring-cyan-500/20 shadow-lg"
            />
            <div className="absolute inset-0 bg-slate-900/40 rounded-2xl flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
              <Camera className="h-6 w-6 text-white" />
            </div>
          </div>

          <div className="flex-1 text-center sm:text-left space-y-2">
            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2.5">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {user?.full_name}
              </h1>

              {/* Role Badge */}
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border shadow-sm ${
                  user?.role === 'admin'
                    ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-700'
                    : 'bg-cyan-100 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 border-cyan-300 dark:border-cyan-700'
                }`}
              >
                {user?.role}
              </span>

              {/* Verified Badge */}
              {user?.is_verified ? (
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                  <ShieldCheck className="h-3.5 w-3.5" /> Verified
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 border border-slate-300 dark:border-zinc-700">
                  Unverified
                </span>
              )}
            </div>

            <p className="text-sm text-slate-500 dark:text-zinc-400 flex items-center justify-center sm:justify-start gap-2">
              <Mail className="h-4 w-4" /> {user?.email}
            </p>

            <p className="text-xs text-slate-400 dark:text-zinc-500">
              Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString(undefined, { month: 'long', year: 'numeric' }) : 'recently'}
            </p>
          </div>
        </div>
      </motion.div>

      {/* ── Form & Settings Grid ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Edit Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-2 glass-card p-6 sm:p-8 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl"
        >
          <div className="flex items-center gap-2 mb-6">
            <UserIcon className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Personal Information</h2>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
            <Input
              label="Full Name"
              type="text"
              leftIcon={<UserIcon className="h-4 w-4 text-slate-400" />}
              error={errors.full_name?.message}
              id="profile-full-name"
              {...register('full_name')}
            />

            <Input
              label="Email Address (Read-only)"
              type="email"
              value={user?.email || ''}
              disabled
              leftIcon={<Mail className="h-4 w-4 text-slate-400" />}
              id="profile-email-readonly"
              className="opacity-75 cursor-not-allowed bg-slate-100 dark:bg-zinc-800"
            />

            <Input
              label="Phone Number"
              type="tel"
              placeholder="+91 98765 43210"
              leftIcon={<Phone className="h-4 w-4 text-slate-400" />}
              error={errors.phone_number?.message}
              id="profile-phone"
              {...register('phone_number')}
            />

            <Input
              label="Location"
              type="text"
              placeholder="e.g. Mumbai, India"
              leftIcon={<MapPin className="h-4 w-4 text-slate-400" />}
              error={errors.location?.message}
              id="profile-location"
              {...register('location')}
            />

            <Input
              label="Profile Image URL"
              type="url"
              placeholder="https://example.com/avatar.jpg"
              leftIcon={<Sparkles className="h-4 w-4 text-slate-400" />}
              error={errors.profile_image?.message}
              id="profile-image-url"
              {...register('profile_image')}
            />

            <div className="pt-2 flex justify-end">
              <Button
                type="submit"
                isLoading={isUpdatingProfile}
                disabled={!isDirty || isUpdatingProfile}
                className="bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-semibold rounded-xl px-6 shadow-md"
              >
                {isUpdatingProfile ? 'Saving Changes...' : 'Save Profile'}
              </Button>
            </div>
          </form>
        </motion.div>

        {/* Security & Account Sidebar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          {/* Security Box */}
          <div className="glass-card p-6 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <KeyRound className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Security</h3>
            </div>

            <p className="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed">
              Want to update your password or refresh security credentials?
            </p>

            <a
              href="/forgot-password"
              className="inline-flex items-center gap-2 text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline pt-1"
            >
              Request Password Reset →
            </a>
          </div>

          {/* Logout Box */}
          <div className="glass-card p-6 rounded-3xl border border-rose-200/60 dark:border-rose-900/30 bg-rose-50/50 dark:bg-rose-950/20 backdrop-blur-xl shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-rose-900 dark:text-rose-200">Sign Out</h3>
            <p className="text-xs text-rose-700 dark:text-rose-300 leading-relaxed">
              End your active session securely.
            </p>
            <Button
              onClick={() => logout()}
              variant="outline"
              leftIcon={<LogOut className="h-4 w-4 text-rose-600" />}
              className="border-rose-300 text-rose-700 hover:bg-rose-100 dark:border-rose-800 dark:text-rose-300 dark:hover:bg-rose-900/40 w-full justify-center rounded-xl"
            >
              Sign Out
            </Button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
