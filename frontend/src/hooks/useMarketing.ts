/**
 * STARTWISE AI — Marketing Strategy TanStack Query Hooks (Stage 9)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { marketingService } from '@/services/marketingService'

export const MARKETING_KEYS = {
  all: ['marketing'] as const,
  strategy: (startupId: string) => ['marketing', 'strategy', startupId] as const,
  channels: (startupId: string) => ['marketing', 'channels', startupId] as const,
  plan: (startupId: string) => ['marketing', 'plan', startupId] as const,
  content: (startupId: string) => ['marketing', 'content', startupId] as const,
}

/** Hook: Fetch latest marketing strategy for a startup idea */
export function useMarketingStrategy(startupId: string, enabled = true) {
  return useQuery({
    queryKey: MARKETING_KEYS.strategy(startupId),
    queryFn: () => marketingService.getLatestStrategy(startupId),
    enabled: !!startupId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}

/** Hook: Analyze and generate personalized marketing strategy */
export function useAnalyzeMarketing() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (startupId: string) => marketingService.analyzeMarketing(startupId),
    onSuccess: (data) => {
      toast.success('AI Marketing Strategy Generated! 🚀')
      if (data.startup_id) {
        queryClient.invalidateQueries({ queryKey: MARKETING_KEYS.strategy(data.startup_id) })
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Marketing analysis failed')
    },
  })
}

/** Hook: Regenerate marketing strategy */
export function useRegenerateMarketing() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (startupId: string) => marketingService.regenerateStrategy(startupId),
    onSuccess: (data) => {
      toast.success('Marketing Strategy Regenerated! 🔄')
      if (data.startup_id) {
        queryClient.invalidateQueries({ queryKey: MARKETING_KEYS.strategy(data.startup_id) })
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Regeneration failed')
    },
  })
}
