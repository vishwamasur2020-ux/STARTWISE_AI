/**
 * STARTWISE AI — Prediction Types (Stage 7)
 */

export interface PredictionAnalysisInput {
  startup_id?: string
  business_name: string
  business_category: string
  business_model?: string
  business_description?: string
  investment_amount: number
  expected_monthly_revenue: number
  expected_monthly_expenses: number
  employee_count?: number
  experience_years?: number
  location: string
  target_customer: string
  market_demand?: number
  competition_level?: 'Low' | 'Medium' | 'High' | string
  funding_source?: string
}

export interface FeatureImportance {
  feature_name: string
  importance: number
}

export interface ModelInformation {
  success_model: string
  risk_model: string
  roi_model: string
  competition_model: string
}

export interface SuccessPrediction {
  prediction: boolean
  probability: number
}

export interface RiskPrediction {
  level: 'Low' | 'Medium' | 'High' | string
  probability: number
}

export interface RoiPrediction {
  estimated_percentage: number
}

export interface CompetitionPrediction {
  level: 'Low' | 'Medium' | 'High' | string
  probability: number
}

export interface PredictionAnalysisResponse {
  id?: string
  startup_id?: string
  business_name: string
  success: SuccessPrediction
  risk: RiskPrediction
  roi: RoiPrediction
  competition: CompetitionPrediction
  business_score: number
  score_label: 'Excellent' | 'Good' | 'Moderate' | 'High Risk' | 'Very High Risk' | string
  recommendations: string[]
  model_information: ModelInformation
  top_features?: FeatureImportance[]
  created_at?: string
}

export interface MlHealthStatus {
  status: 'healthy' | 'unhealthy' | string
  models_loaded: boolean
  models: {
    success: boolean
    risk: boolean
    roi: boolean
    competition: boolean
  }
  error?: string | null
}
