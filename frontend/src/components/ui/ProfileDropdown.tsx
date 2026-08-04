/**
 * STARTWISE AI — Profile Dropdown Component
 */

import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { User, Settings, LogOut, ShieldCheck, ChevronDown } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

export function ProfileDropdown() {
  const [open, setOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const { user, logout } = useAuth()

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const userInitials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : 'US'

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 p-1 rounded-full hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
        aria-label="User profile menu"
      >
        <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-cyan-400 via-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-extrabold shadow-sm">
          {userInitials}
        </div>
        <ChevronDown className="h-4 w-4 text-slate-400 hidden sm:block" />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-56 rounded-2xl glass-card bg-white/95 dark:bg-zinc-900/95 border border-slate-200/80 dark:border-white/10 p-2 shadow-2xl z-50 text-xs">
          <div className="p-3 border-b border-slate-100 dark:border-zinc-800">
            <p className="font-bold text-slate-900 dark:text-white truncate">{user?.full_name || 'User Account'}</p>
            <p className="text-[10px] text-slate-400 truncate">{user?.email}</p>
          </div>

          <div className="py-1 space-y-0.5">
            <Link
              to="/profile"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-700 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-800 font-semibold"
            >
              <User className="h-4 w-4 text-slate-400" /> My Profile
            </Link>
            <Link
              to="/settings"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-700 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-800 font-semibold"
            >
              <Settings className="h-4 w-4 text-slate-400" /> Settings
            </Link>
            {user?.role === 'admin' && (
              <Link
                to="/admin"
                onClick={() => setOpen(false)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/40 font-semibold"
              >
                <ShieldCheck className="h-4 w-4 text-amber-500" /> Admin Portal
              </Link>
            )}
          </div>

          <div className="pt-1 border-t border-slate-100 dark:border-zinc-800">
            <button
              onClick={() => {
                setOpen(false)
                logout()
              }}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 font-semibold"
            >
              <LogOut className="h-4 w-4" /> Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
