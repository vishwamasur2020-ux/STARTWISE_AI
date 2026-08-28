/**
 * STARTWISE AI — Prediction TanStack Query Hooks (Stage 7)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { predictionService } from '@/services/predictionService'
import { PredictionAnalysisInput } from '@/types/prediction'

export const PREDICTION_KEYS = {
  all: ['predictions'] as const,
  detail: (startupId: string) => [...PREDICTION_KEYS.all, 'detail', startupId] as const,
  history: (startupId: string) => [...PREDICTION_KEYS.all, 'history', startupId] as const,
  health: ['ml-health'] as const,
}

/** Hook: Run AI analysis */
export function useAnalyzeStartup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: PredictionAnalysisInput) => predictionService.analyzeStartup(data),
    onSuccess: (data) => {
      toast.success('AI Feasibility Analysis Completed! 🚀')
      if (data.startup_id) {
        queryClient.invalidateQueries({ queryKey: PREDICTION_KEYS.detail(data.startup_id) })
        queryClient.invalidateQueries({ queryKey: PREDICTION_KEYS.history(data.startup_id) })
      }
    },
    onError: (err: any) => {
      const status = err.response?.status
      const url = err.config?.url
      const method = err.config?.method?.toUpperCase() || 'POST'
      const detail = err.response?.data?.detail || err.message || 'Analysis failed'

      console.error(`[Prediction API Error] ${method} ${url} (${status}):`, err.response?.data || err)

      if (status === 404) {
        toast.error(`Prediction API not found: ${method} ${url || '/api/predictions/analyze'}`, { duration: 5000 })
      } else {
        toast.error(`Prediction Failed (${status || 'Error'}): ${detail}`, { duration: 5000 })
      }
    },
  })
}

/** Hook: Fetch latest prediction for a startup */
export function useGetPrediction(startupId: string, enabled = true) {
  return useQuery({
    queryKey: PREDICTION_KEYS.detail(startupId),
    queryFn: () => predictionService.getPrediction(startupId),
    enabled: !!startupId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}

/** Hook: Fetch prediction history for a startup */
export function useGetPredictionHistory(startupId: string, enabled = true) {
  return useQuery({
    queryKey: PREDICTION_KEYS.history(startupId),
    queryFn: () => predictionService.getPredictionHistory(startupId),
    enabled: !!startupId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}

/** Hook: Re-analyze a startup */
export function useReanalyzeStartup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (startupId: string) => predictionService.reanalyzeStartup(startupId),
    onSuccess: (data) => {
      toast.success('Startup Re-Analyzed with Latest ML Models! 🔄')
      if (data.startup_id) {
        queryClient.invalidateQueries({ queryKey: PREDICTION_KEYS.detail(data.startup_id) })
        queryClient.invalidateQueries({ queryKey: PREDICTION_KEYS.history(data.startup_id) })
      }
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || err.message || 'Re-analysis failed'
      toast.error(msg)
    },
  })
}

/** Hook: Inspect ML Engine health */
export function useMlHealth() {
  return useQuery({
    queryKey: PREDICTION_KEYS.health,
    queryFn: () => predictionService.getMlHealth(),
    staleTime: 60 * 1000,
  })
}
