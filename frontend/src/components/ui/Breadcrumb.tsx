/**
 * STARTWISE AI — Breadcrumb Trail Component
 */

import { Link } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'

export interface BreadcrumbItem {
  label: string
  href?: string
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[]
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-zinc-400 mb-4">
      <Link
        to="/dashboard"
        className="flex items-center gap-1 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors"
      >
        <Home className="h-3.5 w-3.5" />
      </Link>
      {items.map((item, idx) => (
        <div key={idx} className="flex items-center gap-1.5">
          <ChevronRight className="h-3.5 w-3.5 text-slate-300 dark:text-zinc-600" />
          {item.href ? (
            <Link
              to={item.href}
              className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors font-medium"
            >
              {item.label}
            </Link>
          ) : (
            <span className="font-semibold text-slate-900 dark:text-white">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  )
}
