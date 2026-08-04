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
    const { data } = await api.post<User>('/auth/register', payload)
    return data
  },

  /** Login and store tokens */
  login: async (payload: LoginPayload): Promise<{ tokens: TokenPair; user: User }> => {
    const { data: tokens } = await api.post<TokenPair>('/auth/login', payload)
    setTokens(tokens.access_token, tokens.refresh_token)
    const { data: user } = await api.get<User>('/auth/me')
    return { tokens, user }
  },

  /** Get current authenticated user */
  getMe: async (): Promise<User> => {
    const { data } = await api.get<User>('/auth/me')
    return data
  },

  /** Refresh token pair */
  refreshToken: async (): Promise<TokenPair> => {
    const currentRefresh = getRefreshToken()
    if (!currentRefresh) throw new Error('No refresh token available')
    const { data: tokens } = await api.post<TokenPair>('/auth/refresh', {
      refresh_token: currentRefresh,
    })
    setTokens(tokens.access_token, tokens.refresh_token)
    return tokens
  },

  /** Logout — revokes backend tokens and clears local tokens */
  logout: async (): Promise<void> => {
    try {
      const currentRefresh = getRefreshToken()
      await api.post<MessageResponse>('/auth/logout', {
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
    const { data } = await api.post<MessageResponse>('/auth/forgot-password', payload)
    return data
  },

  /** Reset password with OTP/token */
  resetPassword: async (payload: ResetPasswordPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/auth/reset-password', payload)
    return data
  },

  /** Update user profile */
  updateProfile: async (payload: UserUpdatePayload): Promise<User> => {
    const { data } = await api.patch<User>('/users/profile', payload)
    return data
  },
}
