/**
 * STARTWISE AI — useTheme Hook
 * Manages light/dark theme with system preference detection.
 */

import { useState, useEffect } from 'react'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Theme } from '@/types'

interface ThemeStore {
  theme: Theme
  setTheme: (theme: Theme) => void
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => set({ theme }),
    }),
    { name: 'startwise-theme' }
  )
)

export function useTheme() {
  const { theme, setTheme } = useThemeStore()
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const applyTheme = (t: Theme) => {
      const resolved =
        t === 'system' ? (mediaQuery.matches ? 'dark' : 'light') : t
      setResolvedTheme(resolved)
      document.documentElement.classList.toggle('dark', resolved === 'dark')
    }

    applyTheme(theme)

    const handler = () => {
      if (theme === 'system') applyTheme('system')
    }
    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [theme])

  return { theme, resolvedTheme, setTheme, isDark: resolvedTheme === 'dark' }
}
