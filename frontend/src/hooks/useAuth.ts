/**
 * STARTWISE AI — useAuth Hook
 * Encapsulates login, register, logout, forgot-password, reset-password, and profile update mutations with TanStack Query.
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
  ForgotPasswordPayload,
  ResetPasswordPayload,
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
    onError: () => setLoading(false),
    onSettled: () => setLoading(false),
  })

  // ── Register ────────────────────────────────────────────────────────────
  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => authService.register(payload),
    onMutate: () => setLoading(true),
    onSuccess: () => {
      toast.success('Account created successfully! Please sign in. 🎉')
      navigate('/login')
    },
    onError: () => setLoading(false),
    onSettled: () => setLoading(false),
  })

  // ── Forgot Password ──────────────────────────────────────────────────────
  const forgotPasswordMutation = useMutation({
    mutationFn: (payload: ForgotPasswordPayload) => authService.forgotPassword(payload),
    onSuccess: (data) => {
      toast.success(data.message || 'Reset link/OTP sent to your email!')
    },
  })

  // ── Reset Password ───────────────────────────────────────────────────────
  const resetPasswordMutation = useMutation({
    mutationFn: (payload: ResetPasswordPayload) => authService.resetPassword(payload),
    onSuccess: (data) => {
      toast.success(data.message || 'Password reset successfully! Please log in.')
      navigate('/login')
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
    forgotPassword: forgotPasswordMutation.mutate,
    isSubmittingForgotPassword: forgotPasswordMutation.isPending,
    resetPassword: resetPasswordMutation.mutate,
    isSubmittingResetPassword: resetPasswordMutation.isPending,
    updateProfile: updateProfileMutation.mutate,
    isUpdatingProfile: updateProfileMutation.isPending,
    logout: logoutMutation.mutate,
    isLoggingOut: logoutMutation.isPending,
  }
}
