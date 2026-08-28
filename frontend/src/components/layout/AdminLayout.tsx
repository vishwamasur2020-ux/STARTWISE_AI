/**
 * STARTWISE AI — Admin Layout (Stage 12)
 * Dedicated layout for all /admin/* pages with AdminSidebar + Navbar.
 */

import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { AdminSidebar } from './AdminSidebar'
import { Navbar } from './Navbar'

const ADMIN_PAGE_TITLES: Record<string, string> = {
  '/admin':              'Admin Control Center',
  '/admin/users':        'User Management',
  '/admin/startups':     'Startup Management',
  '/admin/predictions':  'Prediction Monitoring',
  '/admin/franchises':   'Franchise Management',
  '/admin/marketing':    'Marketing Management',
  '/admin/reports':      'Report Management',
  '/admin/ml':           'ML Model Monitoring',
  '/admin/audit-logs':   'Audit Logs',
  '/admin/analytics':    'Platform Analytics',
  '/admin/settings':     'Platform Settings',
}

export function AdminLayout() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const location = useLocation()

  // Match the most specific path
  const title = Object.entries(ADMIN_PAGE_TITLES)
    .sort((a, b) => b[0].length - a[0].length)
    .find(([path]) => location.pathname.startsWith(path))?.[1] ?? 'Admin Panel'

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex flex-shrink-0">
        <AdminSidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {mobileSidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm z-30 lg:hidden"
              onClick={() => setMobileSidebarOpen(false)}
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed left-0 top-0 h-full z-40 lg:hidden"
            >
              <AdminSidebar />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="bg-slate-900 border-b border-white/10">
          <Navbar
            title={title}
            onMobileMenuToggle={() => setMobileSidebarOpen(v => !v)}
            mobileMenuOpen={mobileSidebarOpen}
          />
        </div>

        <main className="flex-1 overflow-y-auto bg-slate-950">
          <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6 min-h-full">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  )
}
