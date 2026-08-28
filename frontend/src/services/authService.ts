/**
 * STARTWISE AI — Auth API Service
 * Wraps all auth-related HTTP calls for login, register, token refresh, logout, forgot/reset password, and profile updates.
 */

import api, { setTokens, clearTokens, getRefreshToken } from './api'
import type {
  User,
  TokenPair,
  LoginPayload,
  RegisterPayload,
  ForgotPasswordPayload,
  ResetPasswordPayload,
  UserUpdatePayload,
  MessageResponse,
} from '@/types'

export const authService = {
  /** Register a new user */
  register: async (payload: RegisterPayload): Promise<User> => {
    const { data } = await api.post<User>('/api/v1/auth/register', payload)
    return data
  },

  /** Login and store tokens */
  login: async (payload: LoginPayload): Promise<{ tokens: TokenPair; user: User }> => {
    const { data: tokens } = await api.post<TokenPair>('/api/v1/auth/login', payload)
    setTokens(tokens.access_token, tokens.refresh_token)
    const { data: user } = await api.get<User>('/api/v1/auth/me')
    return { tokens, user }
  },

  /** Get current authenticated user */
  getMe: async (): Promise<User> => {
    const { data } = await api.get<User>('/api/v1/auth/me')
    return data
  },

  /** Refresh token pair */
  refreshToken: async (): Promise<TokenPair> => {
    const currentRefresh = getRefreshToken()
    if (!currentRefresh) throw new Error('No refresh token available')
    const { data: tokens } = await api.post<TokenPair>('/api/v1/auth/refresh', {
      refresh_token: currentRefresh,
    })
    setTokens(tokens.access_token, tokens.refresh_token)
    return tokens
  },

  /** Logout — revokes backend tokens and clears local tokens */
  logout: async (): Promise<void> => {
    try {
      const currentRefresh = getRefreshToken()
      await api.post<MessageResponse>('/api/v1/auth/logout', {
        refresh_token: currentRefresh,
      })
    } catch {
      // Ignore network/auth errors on logout
    } finally {
      clearTokens()
    }
  },

  /** Request password reset OTP/token */
  forgotPassword: async (payload: ForgotPasswordPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/api/v1/auth/forgot-password', payload)
    return data
  },

  /** Reset password with OTP/token */
  resetPassword: async (payload: ResetPasswordPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/api/v1/auth/reset-password', payload)
    return data
  },

  /** Update user profile */
  updateProfile: async (payload: UserUpdatePayload): Promise<User> => {
    const { data } = await api.patch<User>('/api/v1/users/profile', payload)
    return data
  },
}
