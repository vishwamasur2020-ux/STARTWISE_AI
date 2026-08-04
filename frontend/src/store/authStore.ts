/**
 * STARTWISE AI — Auth Store (Zustand)
 * Global auth state: user, token status, login/logout actions.
 */

import { create } from 'zustand'
import { persist, devtools } from 'zustand/middleware'
import type { User } from '@/types'
import { getAccessToken } from '@/services/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean

  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  logout: () => void
  checkAuth: () => boolean
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        isAuthenticated: false,
        isLoading: false,

        setUser: (user) =>
          set({ user, isAuthenticated: !!user }, false, 'setUser'),

        setLoading: (loading) =>
          set({ isLoading: loading }, false, 'setLoading'),

        logout: () =>
          set({ user: null, isAuthenticated: false }, false, 'logout'),

        checkAuth: () => {
          const token = getAccessToken()
          if (!token) {
            set({ user: null, isAuthenticated: false })
            return false
          }
          return get().isAuthenticated
        },
      }),
      {
        name: 'startwise-auth',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'AuthStore' }
  )
)
