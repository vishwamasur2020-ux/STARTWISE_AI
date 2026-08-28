/**
 * STARTWISE AI — Admin TanStack Query Hooks (Stage 12)
 * All data fetching and mutations for the Admin Panel.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { adminService } from '@/services/adminService'

// ── Dashboard ─────────────────────────────────────────────────────────────
export function useAdminDashboard() {
  return useQuery({
    queryKey: ['admin', 'dashboard'],
    queryFn: () => adminService.getDashboard(),
    staleTime: 60_000,
  })
}

// ── Users ─────────────────────────────────────────────────────────────────
export function useAdminUsers(params: {
  page?: number
  per_page?: number
  search?: string
  role?: string
  is_active?: boolean
  is_verified?: boolean
} = {}) {
  return useQuery({
    queryKey: ['admin', 'users', params],
    queryFn: () => adminService.getUsers(params),
    staleTime: 30_000,
  })
}

export function useAdminUser(id: string) {
  return useQuery({
    queryKey: ['admin', 'users', id],
    queryFn: () => adminService.getUser(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useUpdateUserStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      adminService.updateUserStatus(id, is_active),
    onSuccess: (_, { is_active }) => {
      toast.success(is_active ? 'User activated successfully.' : 'User deactivated successfully.')
      qc.invalidateQueries({ queryKey: ['admin', 'users'] })
    },
    onError: () => toast.error('Unable to update user status.'),
  })
}

export function useUpdateUserRole() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, role }: { id: string; role: string }) =>
      adminService.updateUserRole(id, role),
    onSuccess: () => {
      toast.success('User role updated successfully.')
      qc.invalidateQueries({ queryKey: ['admin', 'users'] })
    },
    onError: () => toast.error('Unable to update user role.'),
  })
}

export function useDeleteUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => adminService.deleteUser(id),
    onSuccess: () => {
      toast.success('User deleted successfully.')
      qc.invalidateQueries({ queryKey: ['admin', 'users'] })
      qc.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
    },
    onError: () => toast.error('Unable to delete user.'),
  })
}

// ── Startups ──────────────────────────────────────────────────────────────
export function useAdminStartups(params: {
  page?: number
  per_page?: number
  search?: string
  category?: string
  risk_level?: string
} = {}) {
  return useQuery({
    queryKey: ['admin', 'startups', params],
    queryFn: () => adminService.getStartups(params),
    staleTime: 30_000,
  })
}

export function useAdminStartup(id: string) {
  return useQuery({
    queryKey: ['admin', 'startups', id],
    queryFn: () => adminService.getStartup(id),
    enabled: !!id,
  })
}

// ── Predictions ───────────────────────────────────────────────────────────
export function useAdminPredictions(params: {
  page?: number
  per_page?: number
  search?: string
} = {}) {
  return useQuery({
    queryKey: ['admin', 'predictions', params],
    queryFn: () => adminService.getPredictions(params),
    staleTime: 30_000,
  })
}

// ── Franchises ────────────────────────────────────────────────────────────
export function useAdminFranchises(params: {
  page?: number
  per_page?: number
  search?: string
  is_active?: boolean
  industry?: string
} = {}) {
  return useQuery({
    queryKey: ['admin', 'franchises', params],
    queryFn: () => adminService.getFranchises(params),
    staleTime: 30_000,
  })
}

export function useCreateFranchise() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => adminService.createFranchise(data),
    onSuccess: () => {
      toast.success('Franchise created successfully.')
      qc.invalidateQueries({ queryKey: ['admin', 'franchises'] })
      qc.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
    },
    onError: () => toast.error('Unable to create franchise.'),
  })
}

export function useUpdateFranchise() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      adminService.updateFranchise(id, data),
    onSuccess: () => {
      toast.success('Franchise updated successfully.')
      qc.invalidateQueries({ queryKey: ['admin', 'franchises'] })
    },
    onError: () => toast.error('Unable to update franchise.'),
  })
}

export function useDeleteFranchise() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => adminService.deleteFranchise(id),
    onSuccess: () => {
      toast.success('Franchise deleted successfully.')
      qc.invalidateQueries({ queryKey: ['admin', 'franchises'] })
      qc.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
    },
    onError: () => toast.error('Unable to delete franchise.'),
  })
}

export function useToggleFranchiseStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      adminService.toggleFranchiseStatus(id, is_active),
    onSuccess: (_, { is_active }) => {
      toast.success(is_active ? 'Franchise activated.' : 'Franchise deactivated.')
      qc.invalidateQueries({ queryKey: ['admin', 'franchises'] })
    },
    onError: () => toast.error('Unable to update franchise status.'),
  })
}

// ── Marketing ─────────────────────────────────────────────────────────────
export function useAdminMarketing(params: {
  page?: number
  per_page?: number
  search?: string
} = {}) {
  return useQuery({
    queryKey: ['admin', 'marketing', params],
    queryFn: () => adminService.getMarketing(params),
    staleTime: 30_000,
  })
}

export function useDeleteMarketing() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => adminService.deleteMarketing(id),
    onSuccess: () => {
      toast.success('Marketing strategy deleted.')
      qc.invalidateQueries({ queryKey: ['admin', 'marketing'] })
    },
    onError: () => toast.error('Unable to delete marketing strategy.'),
  })
}

// ── Reports ───────────────────────────────────────────────────────────────
export function useAdminReports(params: {
  page?: number
  per_page?: number
  search?: string
} = {}) {
  return useQuery({
    queryKey: ['admin', 'reports', params],
    queryFn: () => adminService.getReports(params),
    staleTime: 30_000,
  })
}

export function useDeleteReport() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => adminService.deleteReport(id),
    onSuccess: () => {
      toast.success('Report deleted successfully.')
      qc.invalidateQueries({ queryKey: ['admin', 'reports'] })
      qc.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
    },
    onError: () => toast.error('Unable to delete report.'),
  })
}

// ── ML ────────────────────────────────────────────────────────────────────
export function useAdminML() {
  return useQuery({
    queryKey: ['admin', 'ml'],
    queryFn: () => adminService.getML(),
    staleTime: 60_000,
  })
}

// ── Audit Logs ────────────────────────────────────────────────────────────
export function useAdminAuditLogs(params: {
  page?: number
  per_page?: number
  action?: string
  resource?: string
  start_date?: string
  end_date?: string
} = {}) {
  return useQuery({
    queryKey: ['admin', 'audit-logs', params],
    queryFn: () => adminService.getAuditLogs(params),
    staleTime: 15_000,
  })
}

// ── Analytics ─────────────────────────────────────────────────────────────
export function useAdminAnalytics(params: {
  start_date?: string
  end_date?: string
  group_by?: string
} = {}) {
  return useQuery({
    queryKey: ['admin', 'analytics', params],
    queryFn: () => adminService.getAnalytics(params),
    staleTime: 60_000,
  })
}

// ── Settings ──────────────────────────────────────────────────────────────
export function useAdminSettings() {
  return useQuery({
    queryKey: ['admin', 'settings'],
    queryFn: () => adminService.getSettings(),
    staleTime: 5 * 60_000,
  })
}
