/**
 * STARTWISE AI — Prediction API Service (Stage 7)
 * Client calls for AI Prediction Engine (/api/v1/predictions and /api/v1/ml).
 */

import api from '@/services/api'
import {
  PredictionAnalysisInput,
  PredictionAnalysisResponse,
  MlHealthStatus,
} from '@/types/prediction'

export const predictionService = {
  /** Run complete AI analysis on business parameters */
  async analyzeStartup(data: PredictionAnalysisInput): Promise<PredictionAnalysisResponse> {
    console.log('[ML Validation Request] POST /api/predictions/analyze', data)
    const res = await api.post<PredictionAnalysisResponse>('/api/predictions/analyze', data)
    return res.data
  },

  /** Get latest prediction result for a startup idea */
  async getPrediction(startupId: string): Promise<PredictionAnalysisResponse> {
    const res = await api.get<PredictionAnalysisResponse>(`/api/predictions/${startupId}`)
    return res.data
  },

  /** Get prediction history log for a startup idea */
  async getPredictionHistory(startupId: string): Promise<PredictionAnalysisResponse[]> {
    const res = await api.get<PredictionAnalysisResponse[]>(`/api/predictions/${startupId}/history`)
    return res.data
  },

  /** Re-run ML analysis on existing startup idea data */
  async reanalyzeStartup(startupId: string): Promise<PredictionAnalysisResponse> {
    const res = await api.post<PredictionAnalysisResponse>(`/api/predictions/${startupId}/reanalyze`)
    return res.data
  },

  /** Inspect ML engine health status */
  async getMlHealth(): Promise<MlHealthStatus> {
    const res = await api.get<MlHealthStatus>('/api/v1/ml/health')
    return res.data
  },
}
