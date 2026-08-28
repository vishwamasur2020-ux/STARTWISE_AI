/**
 * STARTWISE AI — Franchise API Service (Stage 8)
 * Client calls for Franchise catalog and Recommendation endpoints (/api/v1/franchises and /api/v1/recommendations).
 */

import api from '@/services/api'
import {
  FranchiseItem,
  FranchiseFilterParams,
  FranchiseRecommendationRequestInput,
  FranchiseRecommendationResponse,
  FranchiseComparisonResponse,
} from '@/types/franchise'

export const franchiseService = {
  /** List & filter active franchise catalog */
  async listFranchises(params?: FranchiseFilterParams): Promise<FranchiseItem[]> {
    const res = await api.get<FranchiseItem[]>('/api/v1/franchises', { params })
    return res.data
  },

  /** Get unique available categories */
  async getCategories(): Promise<string[]> {
    const res = await api.get<string[]>('/api/v1/franchises/categories')
    return res.data
  },

  /** Get unique available locations */
  async getLocations(): Promise<string[]> {
    const res = await api.get<string[]>('/api/v1/franchises/locations')
    return res.data
  },

  /** Retrieve single franchise details */
  async getFranchiseDetails(id: string): Promise<FranchiseItem> {
    const res = await api.get<FranchiseItem>(`/api/v1/franchises/${id}`)
    return res.data
  },

  /** Compare 2 to 4 franchises side-by-side */
  async compareFranchises(franchiseIds: string[]): Promise<FranchiseComparisonResponse> {
    const res = await api.post<FranchiseComparisonResponse>('/api/v1/franchises/compare', {
      franchise_ids: franchiseIds,
    })
    return res.data
  },

  /** Generate personalized AI franchise recommendations */
  async generateRecommendations(
    data: FranchiseRecommendationRequestInput
  ): Promise<FranchiseRecommendationResponse> {
    const res = await api.post<FranchiseRecommendationResponse>('/api/v1/recommendations/franchises', data)
    return res.data
  },

  /** Get latest recommendations for a startup idea */
  async getLatestRecommendations(startupId: string): Promise<FranchiseRecommendationResponse> {
    const res = await api.get<FranchiseRecommendationResponse>(`/api/v1/recommendations/franchises/${startupId}`)
    return res.data
  },

  /** Refresh recommendations for a startup idea */
  async refreshRecommendations(startupId: string): Promise<FranchiseRecommendationResponse> {
    const res = await api.post<FranchiseRecommendationResponse>(`/api/v1/recommendations/franchises/${startupId}/refresh`)
    return res.data
  },
}
