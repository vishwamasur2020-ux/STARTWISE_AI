/**
 * STARTWISE AI — Custom TanStack Query Hooks for Startup Module
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { startupService } from '@/services/startupService'
import { StartupCreateInput, StartupUpdateInput, StartupFilterParams } from '@/types/startup'

export const STARTUP_KEYS = {
  all: ['startups'] as const,
  lists: () => [...STARTUP_KEYS.all, 'list'] as const,
  list: (params?: StartupFilterParams) => [...STARTUP_KEYS.lists(), params] as const,
  details: () => [...STARTUP_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...STARTUP_KEYS.details(), id] as const,
  recent: () => [...STARTUP_KEYS.all, 'recent'] as const,
  stats: () => [...STARTUP_KEYS.all, 'stats'] as const,
}

/** Hook to fetch paginated/filtered list of startup ideas */
export function useStartups(params?: StartupFilterParams) {
  return useQuery({
    queryKey: STARTUP_KEYS.list(params),
    queryFn: () => startupService.getStartups(params),
  })
}

/** Hook to fetch single startup idea details */
export function useStartupDetails(id: string) {
  return useQuery({
    queryKey: STARTUP_KEYS.detail(id),
    queryFn: () => startupService.getStartupDetails(id),
    enabled: !!id,
  })
}

/** Hook to fetch 5 recent startups for dashboard */
export function useRecentStartups(limit = 5) {
  return useQuery({
    queryKey: STARTUP_KEYS.recent(),
    queryFn: () => startupService.getRecentStartups(limit),
  })
}

/** Hook to fetch dashboard startup statistics */
export function useStartupStats() {
  return useQuery({
    queryKey: STARTUP_KEYS.stats(),
    queryFn: () => startupService.getStartupStats(),
  })
}

/** Mutation hook to create a startup idea */
export function useCreateStartup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: StartupCreateInput) => startupService.createStartup(data),
    onSuccess: () => {
      toast.success('Startup idea created & validated successfully! 🚀')
      queryClient.invalidateQueries({ queryKey: STARTUP_KEYS.all })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || 'Failed to save startup idea.'
      toast.error(msg)
    },
  })
}

/** Mutation hook to update a startup idea */
export function useUpdateStartup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: StartupUpdateInput }) =>
      startupService.updateStartup(id, data),
    onSuccess: (data) => {
      toast.success('Startup idea updated successfully! ✨')
      queryClient.invalidateQueries({ queryKey: STARTUP_KEYS.all })
      queryClient.invalidateQueries({ queryKey: STARTUP_KEYS.detail(data.id) })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || 'Failed to update startup idea.'
      toast.error(msg)
    },
  })
}

/** Mutation hook to delete a startup idea */
export function useDeleteStartup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => startupService.deleteStartup(id),
    onSuccess: () => {
      toast.success('Startup idea deleted.')
      queryClient.invalidateQueries({ queryKey: STARTUP_KEYS.all })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || 'Failed to delete startup idea.'
      toast.error(msg)
    },
  })
}
