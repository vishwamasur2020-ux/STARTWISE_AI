/**
 * STARTWISE AI — Franchise & Recommendation Types (Stage 8)
 */

export interface FranchiseItem {
  id: string
  franchise_name: string
  name?: string
  industry: string
  category?: string
  business_model?: string
  minimum_investment: number
  maximum_investment: number
  min_investment?: number
  max_investment?: number
  roi: number
  expected_roi?: number
  risk_level: 'Low' | 'Medium' | 'High' | string
  city?: string | null
  state?: string | null
  country: string
  experience_required: number
  market_demand: number
  target_customer?: string | null
  website?: string | null
  website_url?: string | null
  contact_email?: string | null
  description?: string | null
  logo_url?: string | null
  advantages?: string[] | null
  disadvantages?: string[] | null
  is_active: boolean
  created_at: string
}

export interface SubScores {
  budget_fit: number
  industry_fit: number
  location_fit: number
  roi_fit: number
  risk_fit: number
  experience_fit: number
  demand_fit: number
}

export interface FranchiseRecommendationItem {
  franchise: FranchiseItem
  match_score: number
  score_label: 'Excellent Match' | 'Strong Match' | 'Good Match' | 'Moderate Match' | 'Weak Match' | string
  ranking_position: number
  recommendation_type: 'PRIMARY' | 'ALTERNATIVE' | string
  explanation: string[]
  sub_scores: SubScores
}

export interface FranchiseRecommendationRequestInput {
  startup_id?: string
  budget: number
  business_category: string
  location: string
  experience_years?: number
  expected_roi?: number
  risk_preference?: string
  target_customer?: string
}

export interface FranchiseRecommendationResponse {
  startup_id?: string | null
  user_budget: number
  category: string
  location: string
  risk_preference: string
  total_recommendations: number
  recommendations: FranchiseRecommendationItem[]
  disclaimer?: string
  created_at?: string
}

export interface FranchiseFilterParams {
  category?: string
  min_investment?: number
  max_investment?: number
  risk_level?: string
  city?: string
  query?: string
}

export interface FranchiseComparisonResponse {
  franchises: FranchiseItem[]
  comparison_matrix: Record<string, Record<string, any>>
}
