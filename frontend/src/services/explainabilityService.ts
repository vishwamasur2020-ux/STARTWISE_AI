/**
 * STARTWISE AI — Explainability API Service (Stage 13 XAI)
 * Axios calls to /api/v1/explainability/* endpoints.
 */

import api from './api'
import type {
  CombinedExplanationResponse,
  SingleModelExplanationResponse,
} from '@/types/explainability'

const BASE = '/api/v1/explainability'

export const explainabilityService = {
  getCombinedExplanation: (predictionId: string): Promise<CombinedExplanationResponse> =>
    api.get(`${BASE}/${predictionId}`).then((r) => r.data),

  getSuccessExplanation: (predictionId: string): Promise<SingleModelExplanationResponse> =>
    api.get(`${BASE}/success/${predictionId}`).then((r) => r.data),

  getRiskExplanation: (predictionId: string): Promise<SingleModelExplanationResponse> =>
    api.get(`${BASE}/risk/${predictionId}`).then((r) => r.data),

  getRoiExplanation: (predictionId: string): Promise<SingleModelExplanationResponse> =>
    api.get(`${BASE}/roi/${predictionId}`).then((r) => r.data),

  getCompetitionExplanation: (predictionId: string): Promise<SingleModelExplanationResponse> =>
    api.get(`${BASE}/competition/${predictionId}`).then((r) => r.data),
}

export default explainabilityService
