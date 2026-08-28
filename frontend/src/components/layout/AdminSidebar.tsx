/**
 * STARTWISE AI — Admin Sidebar (Stage 12)
 * Dedicated sidebar for the Admin Control Center.
 */

import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Users,
  Building2,
  TrendingUp,
  Store,
  Megaphone,
  FileText,
  Brain,
  ClipboardList,
  BarChart3,
  Settings,
  ArrowLeft,
  LogOut,
  ShieldCheck,
} from 'lucide-react'
import { cn } from '@/utils/cn'
import { useAuth } from '@/hooks/useAuth'
import { useState } from 'react'

const ADMIN_NAV = [
  { label: 'Dashboard',   href: '/admin',            icon: LayoutDashboard,  exact: true },
  { label: 'Users',       href: '/admin/users',      icon: Users },
  { label: 'Startups',    href: '/admin/startups',   icon: Building2 },
  { label: 'Predictions', href: '/admin/predictions',icon: TrendingUp },
  { label: 'Franchises',  href: '/admin/franchises', icon: Store },
  { label: 'Marketing',   href: '/admin/marketing',  icon: Megaphone },
  { label: 'Reports',     href: '/admin/reports',    icon: FileText },
  { label: 'ML Models',   href: '/admin/ml',         icon: Brain },
  { label: 'Audit Logs',  href: '/admin/audit-logs', icon: ClipboardList },
  { label: 'Analytics',   href: '/admin/analytics',  icon: BarChart3 },
  { label: 'Settings',    href: '/admin/settings',   icon: Settings },
]

export function AdminSidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const { user, logout } = useAuth()
  const location = useLocation()

  const userInitials = user?.full_name
    ? user.full_name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
    : 'AD'

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 256 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="relative flex flex-col h-full bg-gradient-to-b from-slate-900 via-slate-900 to-slate-800 border-r border-white/10 backdrop-blur-xl z-20 overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/10 flex-shrink-0">
        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-amber-400 via-orange-500 to-red-500 flex items-center justify-center flex-shrink-0 shadow-lg">
          <ShieldCheck className="h-5 w-5 text-white" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              className="leading-none min-w-0"
            >
              <span className="font-extrabold text-sm tracking-tight text-white block">
                ADMIN CENTER
              </span>
              <span className="text-[10px] font-bold text-amber-400 tracking-widest uppercase">
                STARTWISE AI
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
        {ADMIN_NAV.map((item) => {
          const isActive = item.exact
            ? location.pathname === item.href
            : location.pathname.startsWith(item.href)
          const Icon = item.icon

          return (
            <NavLink
              key={item.href}
              to={item.href}
              title={collapsed ? item.label : undefined}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group',
                isActive
                  ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-slate-400 hover:bg-white/5 hover:text-white',
                collapsed && 'justify-center px-0'
              )}
            >
              <Icon className={cn(
                'h-4 w-4 flex-shrink-0 transition-all group-hover:scale-110',
                isActive ? 'text-amber-400' : 'text-slate-500 group-hover:text-slate-300'
              )} />
              {!collapsed && <span className="truncate">{item.label}</span>}
              {isActive && !collapsed && (
                <div className="ml-auto h-1.5 w-1.5 rounded-full bg-amber-400 flex-shrink-0" />
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="border-t border-white/10 p-3 space-y-1 flex-shrink-0">
        {/* Back to User Dashboard */}
        <NavLink
          to="/dashboard"
          title={collapsed ? 'Back to Dashboard' : undefined}
          className={cn(
            'flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-cyan-400 hover:bg-cyan-500/10 transition-colors',
            collapsed && 'justify-center px-0'
          )}
        >
          <ArrowLeft className="h-4 w-4 flex-shrink-0" />
          {!collapsed && <span>Back to Dashboard</span>}
        </NavLink>

        {/* User Info */}
        <div className={cn('flex items-center gap-3 px-2 py-1.5', collapsed && 'justify-center')}>
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-amber-400 to-orange-500 flex items-center justify-center text-white text-xs font-bold shadow-sm flex-shrink-0">
            {userInitials}
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-white truncate">{user?.full_name ?? 'Admin'}</p>
              <p className="text-[10px] text-slate-400 truncate">{user?.email}</p>
            </div>
          )}
        </div>

        <button
          onClick={() => logout()}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-rose-400 hover:bg-rose-500/10 transition-colors',
            collapsed && 'justify-center px-0'
          )}
        >
          <LogOut className="h-4 w-4 flex-shrink-0" />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(c => !c)}
        className="absolute -right-3 top-16 h-6 w-6 rounded-full bg-slate-700 border border-white/20 shadow-lg flex items-center justify-center text-slate-400 hover:text-amber-400 transition-colors z-30"
        aria-label="Toggle sidebar"
      >
        <motion.div animate={{ rotate: collapsed ? 0 : 180 }} transition={{ duration: 0.25 }}>
          <ArrowLeft className="h-3.5 w-3.5" />
        </motion.div>
      </button>
    </motion.aside>
  )
}
