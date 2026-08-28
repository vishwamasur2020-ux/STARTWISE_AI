/**
 * STARTWISE AI — useExplainability Hooks (Stage 13 XAI)
 * TanStack Query hooks for SHAP explanations and decision insights.
 */

import { useQuery } from '@tanstack/react-query'
import { explainabilityService } from '@/services/explainabilityService'

export function useCombinedExplanation(predictionId?: string, enabled = true) {
  return useQuery({
    queryKey: ['xai', 'combined', predictionId],
    queryFn: () => explainabilityService.getCombinedExplanation(predictionId!),
    enabled: !!predictionId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}

export function useSuccessExplanation(predictionId?: string, enabled = true) {
  return useQuery({
    queryKey: ['xai', 'success', predictionId],
    queryFn: () => explainabilityService.getSuccessExplanation(predictionId!),
    enabled: !!predictionId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}

export function useRiskExplanation(predictionId?: string, enabled = true) {
  return useQuery({
    queryKey: ['xai', 'risk', predictionId],
    queryFn: () => explainabilityService.getRiskExplanation(predictionId!),
    enabled: !!predictionId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}

export function useRoiExplanation(predictionId?: string, enabled = true) {
  return useQuery({
    queryKey: ['xai', 'roi', predictionId],
    queryFn: () => explainabilityService.getRoiExplanation(predictionId!),
    enabled: !!predictionId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}

export function useCompetitionExplanation(predictionId?: string, enabled = true) {
  return useQuery({
    queryKey: ['xai', 'competition', predictionId],
    queryFn: () => explainabilityService.getCompetitionExplanation(predictionId!),
    enabled: !!predictionId && enabled,
    staleTime: 5 * 60 * 1000,
  })
}
