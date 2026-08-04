/**
 * STARTWISE AI — Login Page
 * Glassmorphism layout matching landing page theme with Zod validation,
 * password visibility toggle, remember me option, and social login placeholders.
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Mail, Lock, Eye, EyeOff, Sparkles, ArrowRight, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/hooks/useAuth'

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(true)
  const { login, isLoggingIn } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data: LoginForm) => {
    login(data)
  }

  const handleSocialLogin = (provider: string) => {
    toast.success(`${provider} authentication UI initialized (Backend OAuth ready)`)
  }

  return (
    <div className="min-h-screen flex animated-bg text-slate-900 dark:text-white">
      {/* ── Left Hero Panel ─────────────────────────────────────────────────── */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-cyan-600 via-blue-700 to-indigo-800">
        <div className="absolute inset-0 mesh-bg opacity-30" />
        <div className="relative flex flex-col justify-center px-16 text-white z-10">
          <Link to="/" className="flex items-center gap-3 mb-12 group w-fit">
            <div className="h-10 w-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center group-hover:scale-105 transition-transform">
              <Sparkles className="h-6 w-6 text-cyan-200" />
            </div>
            <span className="text-2xl font-extrabold tracking-tight">STARTWISE AI</span>
          </Link>

          <h2 className="text-4xl font-extrabold leading-tight mb-4">
            Your AI-Powered<br />
            Business Co-Founder
          </h2>
          <p className="text-cyan-100 text-lg mb-10 max-w-md leading-relaxed">
            Validate business ideas, generate ROI predictions, match top franchise opportunities, and scale with confidence.
          </p>

          <div className="space-y-4">
            {[
              '94.2% ML Prediction Accuracy',
              'Instant Franchise Matching Engine',
              'AI Marketing & Executive PDF Reports',
            ].map((feature) => (
              <div key={feature} className="flex items-center gap-3">
                <div className="h-6 w-6 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <ShieldCheck className="h-4 w-4 text-cyan-200" />
                </div>
                <span className="text-white/90 text-sm font-medium">{feature}</span>
              </div>
            ))}
          </div>

          {/* Floating testimonial card */}
          <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
            className="mt-14 glass-card border-white/20 p-5 max-w-sm rounded-2xl shadow-2xl backdrop-blur-md bg-white/10"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-cyan-400 to-indigo-400 flex items-center justify-center text-white text-xs font-bold shadow">
                AR
              </div>
              <div>
                <p className="text-sm font-semibold text-white">Arjun Rao</p>
                <p className="text-xs text-cyan-200">Tech Founder & Franchise Owner</p>
              </div>
            </div>
            <p className="text-xs text-white/85 leading-relaxed">
              "STARTWISE AI gave me the exact market demand score and competitor risk profile I needed. Saved me ₹15L in capital."
            </p>
            <div className="flex mt-2 text-xs">{'⭐'.repeat(5)}</div>
          </motion.div>
        </div>
      </div>

      {/* ── Right Form Panel ────────────────────────────────────────────────── */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md glass-card p-8 sm:p-10 rounded-3xl shadow-xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl"
        >
          {/* Mobile Logo */}
          <Link to="/" className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white shadow">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">STARTWISE AI</span>
          </Link>

          <div className="mb-8">
            <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-2">
              Welcome back 👋
            </h1>
            <p className="text-slate-500 dark:text-zinc-400 text-sm">
              Sign in to your account to continue building your startup vision.
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
            <Input
              label="Email address"
              type="email"
              placeholder="you@example.com"
              leftIcon={<Mail className="h-4 w-4 text-slate-400" />}
              error={errors.email?.message}
              required
              id="login-email"
              {...register('email')}
            />

            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              leftIcon={<Lock className="h-4 w-4 text-slate-400" />}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="focus:outline-none text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
              error={errors.password?.message}
              required
              id="login-password"
              {...register('password')}
            />

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-xs font-medium text-slate-600 dark:text-zinc-400 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-slate-300 text-cyan-600 focus:ring-cyan-500 h-4 w-4 cursor-pointer"
                  id="remember-me"
                />
                Remember me
              </label>
              <Link
                to="/forgot-password"
                className="text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              fullWidth
              size="lg"
              isLoading={isLoggingIn}
              rightIcon={<ArrowRight className="h-4 w-4" />}
              className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg shadow-cyan-500/25"
            >
              {isLoggingIn ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-zinc-800" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white dark:bg-zinc-900 px-3 text-slate-400 dark:text-zinc-500 font-medium">
                Or continue with
              </span>
            </div>
          </div>

          {/* Social Logins */}
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleSocialLogin('Google')}
              className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-xs font-semibold text-slate-700 dark:text-zinc-200 hover:bg-slate-50 dark:hover:bg-zinc-700/50 transition-colors shadow-sm"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.26v3.15C3.25 21.3 7.31 24 12 24z"/>
                <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.26C.46 8.17 0 9.99 0 12s.46 3.83 1.26 5.42l4.02-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.25 2.7 1.26 6.58l4.02 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
              </svg>
              Google
            </button>

            <button
              type="button"
              onClick={() => handleSocialLogin('GitHub')}
              className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border border-slate-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-xs font-semibold text-slate-700 dark:text-zinc-200 hover:bg-slate-50 dark:hover:bg-zinc-700/50 transition-colors shadow-sm"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              GitHub
            </button>
          </div>

          <p className="text-center text-xs text-slate-500 dark:text-zinc-400 mt-8">
            Don't have an account?{' '}
            <Link to="/register" className="font-bold text-cyan-600 dark:text-cyan-400 hover:underline">
              Create a free account
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  )
}
