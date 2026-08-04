/**
 * STARTWISE AI — Sidebar Layout Component
 * Responsive collapsible sidebar with navigation items and role-based links.
 */

import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  BrainCircuit,
  Store,
  Megaphone,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  LogOut,
  User as UserIcon,
  ShieldCheck,
} from 'lucide-react'
import { cn } from '@/utils/cn'
import { useAuth } from '@/hooks/useAuth'

const NAV_GROUPS = [
  {
    group: 'Main',
    items: [
      { label: 'Dashboard',    href: '/dashboard',          icon: LayoutDashboard },
      { label: 'AI Validation', href: '/startup-validation', icon: BrainCircuit },
    ],
  },
  {
    group: 'Discover & Scale',
    items: [
      { label: 'Franchise Hub',  href: '/franchise', icon: Store },
      { label: 'Marketing Plans', href: '/marketing', icon: Megaphone },
      { label: 'PDF Reports',     href: '/reports',   icon: FileText },
    ],
  },
  {
    group: 'Account',
    items: [
      { label: 'My Profile',     href: '/profile',   icon: UserIcon },
      { label: 'Settings',       href: '/settings',  icon: Settings },
    ],
  },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const { user, logout } = useAuth()
  const location = useLocation()

  const userInitials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'US'

  return (
    <motion.aside
      animate={{ width: collapsed ? 76 : 260 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="relative flex flex-col h-full glass-card bg-white/85 dark:bg-zinc-900/85 border-r border-slate-200/80 dark:border-white/10 backdrop-blur-xl z-20"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-200/80 dark:border-zinc-800">
        <NavLink to="/dashboard" className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-md text-white">
            <Sparkles className="h-5 w-5" />
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                className="leading-none"
              >
                <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-white block">
                  STARTWISE
                </span>
                <span className="text-[10px] font-bold text-cyan-600 dark:text-cyan-400 tracking-widest uppercase">
                  AI PLATFORM
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </NavLink>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 overflow-y-auto py-5 px-3 space-y-6">
        {NAV_GROUPS.map((group) => (
          <div key={group.group}>
            {!collapsed && (
              <p className="px-3 mb-2 text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-widest">
                {group.group}
              </p>
            )}
            <ul className="space-y-1">
              {group.items.map((item) => {
                const isActive = location.pathname === item.href || (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
                const Icon = item.icon

                return (
                  <li key={item.href}>
                    <NavLink
                      to={item.href}
                      title={collapsed ? item.label : undefined}
                      className={cn(
                        'flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all group',
                        isActive
                          ? 'bg-gradient-to-r from-cyan-500/15 to-indigo-500/15 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20 shadow-sm'
                          : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-800/60 hover:text-slate-900 dark:hover:text-white',
                        collapsed && 'justify-center px-0'
                      )}
                    >
                      <Icon className={cn('h-4 w-4 flex-shrink-0 transition-transform group-hover:scale-110', isActive ? 'text-cyan-600 dark:text-cyan-400' : 'text-slate-400 dark:text-zinc-500')} />
                      {!collapsed && <span className="truncate">{item.label}</span>}
                    </NavLink>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}

        {/* Admin Link if Admin Role */}
        {user?.role === 'admin' && (
          <div>
            {!collapsed && (
              <p className="px-3 mb-2 text-[10px] font-bold text-amber-500 uppercase tracking-widest">
                Administration
              </p>
            )}
            <NavLink
              to="/admin"
              className={cn(
                'flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/40',
                collapsed && 'justify-center px-0'
              )}
            >
              <ShieldCheck className="h-4 w-4 flex-shrink-0 text-amber-500" />
              {!collapsed && <span>Admin Portal</span>}
            </NavLink>
          </div>
        )}
      </nav>

      {/* User Info & Logout */}
      <div className="border-t border-slate-200/80 dark:border-zinc-800 p-3 space-y-2">
        <div className={cn('flex items-center gap-3 px-2 py-1.5', collapsed && 'justify-center')}>
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-cyan-400 to-indigo-500 flex items-center justify-center text-white text-xs font-bold shadow-sm">
            {userInitials}
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-slate-900 dark:text-white truncate">
                {user?.full_name ?? 'User Account'}
              </p>
              <p className="text-[10px] text-slate-400 dark:text-zinc-500 truncate">{user?.email}</p>
            </div>
          )}
        </div>

        <button
          onClick={() => logout()}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors',
            collapsed && 'justify-center px-0'
          )}
        >
          <LogOut className="h-4 w-4 flex-shrink-0" />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>

      {/* Collapse Toggle Button */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="absolute -right-3 top-16 h-6 w-6 rounded-full bg-white dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 shadow-md flex items-center justify-center text-slate-500 hover:text-cyan-600 transition-colors z-30"
        aria-label="Toggle sidebar collapse"
      >
        {collapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronLeft className="h-3.5 w-3.5" />}
      </button>
    </motion.aside>
  )
}
