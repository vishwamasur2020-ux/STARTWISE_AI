/**
 * STARTWISE AI — 404 Not Found Page
 */

import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Home, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center animated-bg p-8">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md"
      >
        <div className="text-[120px] font-black gradient-text leading-none mb-6">404</div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white mb-3">
          Page not found
        </h1>
        <p className="text-slate-500 dark:text-zinc-400 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex gap-3 justify-center">
          <Button onClick={() => window.history.back()} variant="secondary" leftIcon={<ArrowLeft className="h-4 w-4" />}>
            Go Back
          </Button>
          <Link to="/">
            <Button leftIcon={<Home className="h-4 w-4" />}>
              Home
            </Button>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
