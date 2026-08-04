/**
 * STARTWISE AI — Dashboard Layout
 * Wraps all protected pages with Sidebar + Navbar.
 */

import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Sidebar } from './Sidebar'
import { Navbar } from './Navbar'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard':  'Dashboard',
  '/validate':   'Validate Your Idea',
  '/franchises': 'Franchise Finder',
  '/marketing':  'Marketing Strategy',
  '/reports':    'Reports',
  '/profile':    'My Profile',
  '/settings':   'Settings',
}

export function DashboardLayout() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] ?? 'STARTWISE AI'

  return (
    <div className="flex h-screen overflow-hidden animated-bg">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex flex-shrink-0">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {mobileSidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden"
              onClick={() => setMobileSidebarOpen(false)}
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed left-0 top-0 h-full z-40 lg:hidden"
            >
              <Sidebar />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar
          title={title}
          onMobileMenuToggle={() => setMobileSidebarOpen((v) => !v)}
          mobileMenuOpen={mobileSidebarOpen}
        />

        <main className="flex-1 overflow-y-auto">
          <div className="page-container py-6 min-h-full">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.25, ease: 'easeOut' }}
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
