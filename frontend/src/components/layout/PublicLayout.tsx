/**
 * STARTWISE AI — Public & Main Layout Components
 */

import { Outlet } from 'react-router-dom'

export function PublicLayout() {
  return (
    <div className="min-h-screen flex flex-col animated-bg text-slate-900 dark:text-white">
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}

export function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col animated-bg text-slate-900 dark:text-white">
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
