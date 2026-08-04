/**
 * STARTWISE AI — Top Navbar Component
 * Fixed top bar with search, theme toggle, and user menu.
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Bell, Sun, Moon, Menu, X } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { ProfileDropdown } from '@/components/ui/ProfileDropdown'
import { cn } from '@/utils/cn'

interface NavbarProps {
  onMobileMenuToggle?: () => void
  mobileMenuOpen?: boolean
  title?: string
}

export function Navbar({ onMobileMenuToggle, mobileMenuOpen, title }: NavbarProps) {
  const { isDark, setTheme } = useTheme()
  const [searchFocused, setSearchFocused] = useState(false)

  return (
    <header className="sticky top-0 z-10 frosted border-b border-slate-200 dark:border-zinc-800 px-4 sm:px-6 h-16 flex items-center gap-4">
      {/* Mobile Menu Toggle */}
      <button
        onClick={onMobileMenuToggle}
        className="lg:hidden btn-ghost p-2"
        aria-label="Toggle menu"
      >
        {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Page Title */}
      {title && (
        <h1 className="text-lg font-bold text-slate-900 dark:text-white hidden sm:block">
          {title}
        </h1>
      )}

      {/* Search */}
      <div className="flex-1 max-w-md ml-2">
        <motion.div
          animate={{ scale: searchFocused ? 1.01 : 1 }}
          className="relative"
        >
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search analyses, reports..."
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
            className={cn(
              'w-full pl-9 pr-4 py-2 rounded-xl text-sm',
              'bg-slate-100 dark:bg-zinc-800 border border-transparent',
              'text-slate-800 dark:text-slate-200 placeholder-slate-400',
              'focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500',
              'transition-all duration-200'
            )}
            id="navbar-search"
          />
        </motion.div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2 ml-auto">
        {/* Theme Toggle */}
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={() => setTheme(isDark ? 'light' : 'dark')}
          className="btn-ghost p-2.5 rounded-xl"
          aria-label="Toggle theme"
        >
          {isDark ? (
            <Sun className="h-5 w-5 text-amber-400" />
          ) : (
            <Moon className="h-5 w-5 text-slate-600" />
          )}
        </motion.button>

        {/* Notifications */}
        <motion.button
          whileTap={{ scale: 0.9 }}
          className="btn-ghost p-2.5 rounded-xl relative"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-zinc-900" />
        </motion.button>

        {/* Profile Dropdown */}
        <ProfileDropdown />
      </div>
    </header>
  )
}
