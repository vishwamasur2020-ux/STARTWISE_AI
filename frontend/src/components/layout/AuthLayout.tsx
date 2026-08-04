/**
 * STARTWISE AI — Auth Layout Component
 * Layout container for Login, Register, Forgot Password, and Reset Password pages.
 */

import { Outlet, Link } from 'react-router-dom'
import { Sparkles } from 'lucide-react'

export function AuthLayout() {
  return (
    <div className="min-h-screen animated-bg flex flex-col justify-between py-12 px-4 sm:px-6 lg:px-8 text-slate-900 dark:text-white">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center gap-3 group">
          <div className="h-11 w-11 rounded-2xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-xl shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <Sparkles className="h-6 w-6" />
          </div>
          <span className="text-2xl font-black tracking-tight">STARTWISE AI</span>
        </Link>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Outlet />
      </div>

      <div className="text-center text-xs text-slate-400 dark:text-zinc-500 mt-8">
        STARTWISE AI © 2026 — Next-Gen AI Startup Platform
      </div>
    </div>
  )
}
