/**
 * STARTWISE AI — useAuth Hook
 * Encapsulates authentication, email verification, password reset, and session state.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

import { authService } from '@/services/authService'
import { useAuthStore } from '@/store/authStore'
import { clearTokens } from '@/services/api'
import type {
  LoginPayload,
  RegisterPayload,
  VerifyEmailPayload,
  ResendOTPPayload,
  VerifyResetOTPPayload,
  ForgotPasswordPayload,
  ResetPasswordPayload,
  ChangePasswordPayload,
  UserUpdatePayload,
} from '@/types'

export function useAuth() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, isAuthenticated, setUser, setLoading, logout: storeLogout } = useAuthStore()

  // ── Get current user profile ──────────────────────────────────────────────
  const { isLoading: isFetchingUser, refetch: refetchUser } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      try {
        const userData = await authService.getMe()
        setUser(userData)
        return userData
      } catch (err) {
        storeLogout()
        clearTokens()
        throw err
      }
    },
    enabled: isAuthenticated,
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  // ── Login ───────────────────────────────────────────────────────────────
  const loginMutation = useMutation({
    mutationFn: (payload: LoginPayload) => authService.login(payload),
    onMutate: () => setLoading(true),
    onSuccess: ({ user }) => {
      setUser(user)
      queryClient.invalidateQueries({ queryKey: ['auth'] })
      toast.success(`Welcome back, ${user.full_name.split(' ')[0]}! 🚀`)
      navigate('/dashboard')
    },
    onError: (error: any, variables) => {
      setLoading(false)
      const errDetail = error.response?.data?.detail
      const errCode = error.response?.data?.error_code
      if (errDetail === 'EMAIL_NOT_VERIFIED' || errCode === 'EMAIL_NOT_VERIFIED') {
        const unverifiedEmail = error.response?.data?.email || variables.email
        toast.error('Account unverified. Please enter your verification code.')
        navigate('/verify-email', { state: { email: unverifiedEmail } })
      }
    },
    onSettled: () => setLoading(false),
  })

  // ── Register ────────────────────────────────────────────────────────────
  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => authService.register(payload),
    onMutate: () => setLoading(true),
    onSuccess: (_data, variables) => {
      toast.success('Verification code sent to your email! ✉️')
      navigate('/verify-email', { state: { email: variables.email } })
    },
    onError: () => setLoading(false),
    onSettled: () => setLoading(false),
  })

  // ── Verify Email ─────────────────────────────────────────────────────────
  const verifyEmailMutation = useMutation({
    mutationFn: (payload: VerifyEmailPayload) => authService.verifyEmail(payload),
  })

  // ── Resend OTP ───────────────────────────────────────────────────────────
  const resendOTPMutation = useMutation({
    mutationFn: (payload: ResendOTPPayload) => authService.resendOTP(payload),
    onSuccess: (data) => {
      toast.success(data.message || 'Verification code sent!')
    },
  })

  // ── Forgot Password ──────────────────────────────────────────────────────
  const forgotPasswordMutation = useMutation({
    mutationFn: (payload: ForgotPasswordPayload) => authService.forgotPassword(payload),
    onSuccess: (data, variables) => {
      toast.success(data.message || 'Verification code sent if account exists!')
      navigate('/reset-password', { state: { email: variables.email } })
    },
  })

  // ── Verify Reset OTP ─────────────────────────────────────────────────────
  const verifyResetOTPMutation = useMutation({
    mutationFn: (payload: VerifyResetOTPPayload) => authService.verifyResetOTP(payload),
  })

  // ── Reset Password ───────────────────────────────────────────────────────
  const resetPasswordMutation = useMutation({
    mutationFn: (payload: ResetPasswordPayload) => authService.resetPassword(payload),
    onSuccess: (data) => {
      toast.success(data.message || 'Password reset successfully! Please log in.')
      navigate('/login')
    },
  })

  // ── Change Password (Logged In) ──────────────────────────────────────────
  const changePasswordMutation = useMutation({
    mutationFn: (payload: ChangePasswordPayload) => authService.changePassword(payload),
    onSuccess: (data) => {
      toast.success(data.message || 'Password changed successfully! ✨')
    },
  })

  // ── Update Profile ───────────────────────────────────────────────────────
  const updateProfileMutation = useMutation({
    mutationFn: (payload: UserUpdatePayload) => authService.updateProfile(payload),
    onSuccess: (updatedUser) => {
      setUser(updatedUser)
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] })
      toast.success('Profile updated successfully! ✨')
    },
  })

  // ── Logout ──────────────────────────────────────────────────────────────
  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      storeLogout()
      queryClient.clear()
      toast.success('Logged out successfully.')
      navigate('/login')
    },
  })

  return {
    user,
    isAuthenticated,
    isFetchingUser,
    refetchUser,
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    register: registerMutation.mutate,
    registerAsync: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    verifyEmail: verifyEmailMutation.mutate,
    verifyEmailAsync: verifyEmailMutation.mutateAsync,
    isVerifyingEmail: verifyEmailMutation.isPending,
    resendOTP: resendOTPMutation.mutate,
    resendOTPAsync: resendOTPMutation.mutateAsync,
    isResendingOTP: resendOTPMutation.isPending,
    forgotPassword: forgotPasswordMutation.mutate,
    forgotPasswordAsync: forgotPasswordMutation.mutateAsync,
    isSubmittingForgotPassword: forgotPasswordMutation.isPending,
    verifyResetOTP: verifyResetOTPMutation.mutate,
    verifyResetOTPAsync: verifyResetOTPMutation.mutateAsync,
    isVerifyingResetOTP: verifyResetOTPMutation.isPending,
    resetPassword: resetPasswordMutation.mutate,
    resetPasswordAsync: resetPasswordMutation.mutateAsync,
    isSubmittingResetPassword: resetPasswordMutation.isPending,
    changePassword: changePasswordMutation.mutate,
    changePasswordAsync: changePasswordMutation.mutateAsync,
    isChangingPassword: changePasswordMutation.isPending,
    updateProfile: updateProfileMutation.mutate,
    isUpdatingProfile: updateProfileMutation.isPending,
    logout: logoutMutation.mutate,
    isLoggingOut: logoutMutation.isPending,
  }
}
