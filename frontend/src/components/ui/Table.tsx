/**
 * STARTWISE AI — Table Component
 */

import { HTMLAttributes, TableHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/cn'

export const Table = forwardRef<HTMLTableElement, TableHTMLAttributes<HTMLTableElement>>(
  ({ className, ...props }, ref) => (
    <div className="relative w-full overflow-auto">
      <table ref={ref} className={cn('w-full caption-bottom text-sm border-collapse', className)} {...props} />
    </div>
  )
)
Table.displayName = 'Table'

export const TableHeader = forwardRef<HTMLTableSectionElement, HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <thead ref={ref} className={cn('[&_tr]:border-b border-slate-200 dark:border-zinc-800 text-xs font-bold uppercase tracking-wider text-slate-400', className)} {...props} />
  )
)
TableHeader.displayName = 'TableHeader'

export const TableBody = forwardRef<HTMLTableSectionElement, HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <tbody ref={ref} className={cn('[&_tr:last-child]:border-0 divide-y divide-slate-100 dark:divide-zinc-800', className)} {...props} />
  )
)
TableBody.displayName = 'TableBody'

export const TableRow = forwardRef<HTMLTableRowElement, HTMLAttributes<HTMLTableRowElement>>(
  ({ className, ...props }, ref) => (
    <tr
      ref={ref}
      className={cn('transition-colors hover:bg-slate-50/60 dark:hover:bg-zinc-800/40 data-[state=selected]:bg-slate-100', className)}
      {...props}
    />
  )
)
TableRow.displayName = 'TableRow'

export const TableHead = forwardRef<HTMLTableCellElement, HTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <th ref={ref} className={cn('h-11 px-4 text-left align-middle font-bold text-slate-400 dark:text-zinc-500', className)} {...props} />
  )
)
TableHead.displayName = 'TableHead'

export const TableCell = forwardRef<HTMLTableCellElement, HTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <td ref={ref} className={cn('p-4 align-middle text-slate-800 dark:text-zinc-200', className)} {...props} />
  )
)
TableCell.displayName = 'TableCell'
