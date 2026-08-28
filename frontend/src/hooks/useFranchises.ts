/**
 * STARTWISE AI — Franchise & Recommendation TanStack Query Hooks (Stage 8)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { franchiseService } from '@/services/franchiseService'
import { FranchiseFilterParams, FranchiseRecommendationRequestInput } from '@/types/franchise'

export const FRANCHISE_KEYS = {
  all: ['franchises'] as const,
  list: (params?: FranchiseFilterParams) => ['franchises', 'list', params] as const,
  categories: ['franchises', 'categories'] as const,
  locations: ['franchises', 'locations'] as const,
  detail: (id: string) => ['franchises', 'detail', id] as const,
  recommendations: (startupId: string) => ['franchises', 'recommendations', startupId] as const,
}

/** Hook: Fetch filtered franchises catalog */
export function useFranchises(params?: FranchiseFilterParams) {
  return useQuery({
    queryKey: FRANCHISE_KEYS.list(params),
    queryFn: () => franchiseService.listFranchises(params),
    staleTime: 5 * 60 * 1000,
  })
}

/** Hook: Fetch available categories */
export function useFranchiseCategories() {
  return useQuery({
    queryKey: FRANCHISE_KEYS.categories,
    queryFn: () => franchiseService.getCategories(),
    staleTime: 30 * 60 * 1000,
  })
}

/** Hook: Fetch available locations */
export function useFranchiseLocations() {
  return useQuery({
    queryKey: FRANCHISE_KEYS.locations,
    queryFn: () => franchiseService.getLocations(),
    staleTime: 30 * 60 * 1000,
  })
}

/** Hook: Fetch single franchise details */
export function useFranchiseDetails(id: string, enabled = true) {
  return useQuery({
    queryKey: FRANCHISE_KEYS.detail(id),
    queryFn: () => franchiseService.getFranchiseDetails(id),
    enabled: !!id && enabled,
  })
}

/** Hook: Side-by-side franchise comparison */
export function useCompareFranchises() {
  return useMutation({
    mutationFn: (franchiseIds: string[]) => franchiseService.compareFranchises(franchiseIds),
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Comparison failed')
    },
  })
}

/** Hook: Generate personalized AI recommendations */
export function useGenerateRecommendations() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: FranchiseRecommendationRequestInput) => franchiseService.generateRecommendations(data),
    onSuccess: (data) => {
      toast.success('Franchises Matched & Ranked! 🎯')
      if (data.startup_id) {
        queryClient.invalidateQueries({ queryKey: FRANCHISE_KEYS.recommendations(data.startup_id) })
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Recommendation calculation failed')
    },
  })
}

/** Hook: Fetch latest recommendations for startup */
export function useGetLatestRecommendations(startupId: string, enabled = true) {
  return useQuery({
    queryKey: FRANCHISE_KEYS.recommendations(startupId),
    queryFn: () => franchiseService.getLatestRecommendations(startupId),
    enabled: !!startupId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}

/** Hook: Refresh recommendations for startup */
export function useRefreshRecommendations() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (startupId: string) => franchiseService.refreshRecommendations(startupId),
    onSuccess: (data) => {
      toast.success('Recommendations Refreshed! 🔄')
      if (data.startup_id) {
        queryClient.invalidateQueries({ queryKey: FRANCHISE_KEYS.recommendations(data.startup_id) })
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Refresh failed')
    },
  })
}
