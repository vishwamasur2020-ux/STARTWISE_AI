import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Merge Tailwind classes intelligently — resolves conflicts */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Format currency (INR) */
export function formatCurrency(value: number, currency = 'INR'): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value)
}

/** Format percentage */
export function formatPercent(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`
}

/** Format large numbers (1200 → 1.2K) */
export function formatCompact(value: number): string {
  return new Intl.NumberFormat('en', { notation: 'compact' }).format(value)
}

/** Get risk color class */
export function getRiskColor(risk: string): string {
  switch (risk?.toLowerCase()) {
    case 'low':    return 'badge-success'
    case 'medium': return 'badge-warning'
    case 'high':   return 'badge-danger'
    default:       return 'badge-info'
  }
}

/** Get score color (0–100) */
export function getScoreColor(score: number): string {
  if (score >= 70) return '#10B981'  // emerald
  if (score >= 40) return '#F59E0B'  // amber
  return '#EF4444'                    // red
}

/** Clamp a number between min and max */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

/** Truncate text with ellipsis */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return `${text.slice(0, maxLength)}...`
}

/** Format date to readable string */
export function formatDate(dateString: string): string {
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(dateString))
}

/** Format date with time */
export function formatDateTime(dateString: string): string {
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateString))
}

/** Generate initials from name */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

/** Sleep utility for demos */
export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

/** Debounce function */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

/** Check if value is empty (null, undefined, '', [], {}) */
export function isEmpty(value: unknown): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value as object).length === 0
  return false
}
