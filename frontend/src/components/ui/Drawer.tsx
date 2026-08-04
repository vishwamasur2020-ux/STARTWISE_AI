/**
 * STARTWISE AI — Drawer Component
 * Slide-over navigation/filter drawer powered by Framer Motion.
 */

import { ReactNode, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'

export interface DrawerProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  position?: 'left' | 'right'
}

export function Drawer({
  isOpen,
  onClose,
  title,
  children,
  position = 'right',
}: DrawerProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  const slideVariants = {
    left: { hidden: { x: '-100%' }, visible: { x: 0 } },
    right: { hidden: { x: '100%' }, visible: { x: 0 } },
  }

  const positionStyles = {
    left: 'left-0 border-r',
    right: 'right-0 border-l',
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
          />

          {/* Drawer Content Panel */}
          <motion.aside
            initial="hidden"
            animate="visible"
            exit="hidden"
            variants={slideVariants[position]}
            transition={{ type: 'spring', damping: 30, stiffness: 350 }}
            className={`absolute top-0 bottom-0 w-full max-w-sm glass-card bg-white/95 dark:bg-zinc-900/95 border-slate-200 dark:border-white/10 p-6 shadow-2xl flex flex-col z-10 ${positionStyles[position]}`}
          >
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-200 dark:border-zinc-800">
              <h3 className="font-bold text-lg text-slate-900 dark:text-white">{title || 'Menu'}</h3>
              <button
                onClick={onClose}
                className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-zinc-800"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto">{children}</div>
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  )
}
