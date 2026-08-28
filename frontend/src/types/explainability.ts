/**
 * STARTWISE AI — Explainable AI (XAI) TypeScript Interfaces (Stage 13)
 */

export interface FeatureImpactItem {
  feature_name: string
  display_name: string
  category: string
  impact_value: number
  direction: 'positive' | 'negative' | 'neutral'
  user_value?: string | number | null
  description: string
}

export interface FactorItem {
  feature: string
  display_name: string
  impact: number
  direction: 'positive' | 'negative'
  description: string
  user_value?: string | number | null
}

export interface ModelTransparencyInfo {
  model_name: string
  algorithm: string
  model_version: string
  explanation_method: string
  features_used: number
  prediction_date?: string | null
}

export interface SingleModelExplanationResponse {
  prediction_id: string
  model_name: string
  target_metric: string
  predicted_value: any
  probability?: number | null
  model_info: ModelTransparencyInfo
  top_positive_factors: FactorItem[]
  top_negative_factors: FactorItem[]
  feature_contributions: FeatureImpactItem[]
  summary: string
  disclaimer: string
}

export interface PipelineStep {
  step_number: number
  title: string
  description: string
}

export interface CombinedExplanationResponse {
  prediction_id: string
  startup_id: string
  business_name: string
  business_score: number
  score_label: string
  success: SingleModelExplanationResponse
  risk: SingleModelExplanationResponse
  roi: SingleModelExplanationResponse
  competition: SingleModelExplanationResponse
  overall_decision_summary: string
  top_positive_factors: FactorItem[]
  top_negative_factors: FactorItem[]
  pipeline_steps: PipelineStep[]
  disclaimer: string
}
