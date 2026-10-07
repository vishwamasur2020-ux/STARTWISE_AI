/**
 * STARTWISE AI — Auth API Service
 * Wraps all auth-related HTTP calls:
 * - Register (returns OTP sent response)
 * - Verify Email OTP
 * - Resend OTP
 * - Login & Token storage
 * - Forgot Password OTP
 * - Verify Reset OTP
 * - Reset Password
 * - Change Password (authenticated)
 * - Verification Status
 * - Token Refresh & Logout
 */

import api, { setTokens, clearTokens, getRefreshToken } from './api'
import type {
  User,
  TokenPair,
  LoginPayload,
  RegisterPayload,
  RegisterResponse,
  VerifyEmailPayload,
  ResendOTPPayload,
  VerifyResetOTPPayload,
  ForgotPasswordPayload,
  ResetPasswordPayload,
  ChangePasswordPayload,
  VerificationStatus,
  UserUpdatePayload,
  MessageResponse,
} from '@/types'

export const authService = {
  /** Register a new user account (unverified, triggers OTP email) */
  register: async (payload: RegisterPayload): Promise<RegisterResponse> => {
    const { data } = await api.post<RegisterResponse>('/api/v1/auth/register', payload)
    return data
  },

  /** Verify account email with 6-digit OTP */
  verifyEmail: async (payload: VerifyEmailPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/api/v1/auth/verify-email', payload)
    return data
  },

  /** Resend verification or password reset OTP with cooldown */
  resendOTP: async (payload: ResendOTPPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/api/v1/auth/resend-otp', payload)
    return data
  },

  /** Login and store tokens */
  login: async (payload: LoginPayload): Promise<{ tokens: TokenPair; user: User }> => {
    const { data: tokens } = await api.post<TokenPair>('/api/v1/auth/login', payload)
    setTokens(tokens.access_token, tokens.refresh_token)
    const { data: user } = await api.get<User>('/api/v1/auth/me')
    return { tokens, user }
  },

  /** Get current authenticated user profile */
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

  /** Logout — revokes backend tokens and clears local storage */
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

  /** Request password reset OTP/link */
  forgotPassword: async (payload: ForgotPasswordPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/api/v1/auth/forgot-password', payload)
    return data
  },

  /** Preliminary verify reset OTP */
  verifyResetOTP: async (payload: VerifyResetOTPPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/api/v1/auth/verify-reset-otp', payload)
    return data
  },

  /** Reset password with OTP */
  resetPassword: async (payload: ResetPasswordPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/api/v1/auth/reset-password', payload)
    return data
  },

  /** Change password for logged-in user */
  changePassword: async (payload: ChangePasswordPayload): Promise<MessageResponse> => {
    const { data } = await api.post<MessageResponse>('/api/v1/auth/change-password', payload)
    return data
  },

  /** Get verification status for an email */
  getVerificationStatus: async (email: string): Promise<VerificationStatus> => {
    const { data } = await api.get<VerificationStatus>(`/api/v1/auth/verification-status?email=${encodeURIComponent(email)}`)
    return data
  },

  /** Update user profile */
  updateProfile: async (payload: UserUpdatePayload): Promise<User> => {
    const { data } = await api.patch<User>('/api/v1/users/profile', payload)
    return data
  },
}
