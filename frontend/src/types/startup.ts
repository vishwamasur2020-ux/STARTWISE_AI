/**
 * STARTWISE AI — Startup Module Types & Interfaces
 */

export interface StartupIdea {
  id: string
  user_id: string
  business_name: string
  business_category: string
  business_model: string
  investment_amount: number
  preferred_location: string
  target_customers: string
  experience_years: number
  expected_monthly_revenue: number
  market_demand: number
  competition_level: string
  employee_count: number
  description?: string
  created_at: string
  updated_at?: string
  prediction_result?: any
}

export interface StartupCreateInput {
  business_name: string
  business_category: string
  business_model: string
  investment_amount: number
  preferred_location: string
  target_customers: string
  experience_years?: number
  expected_monthly_revenue?: number
  expected_expenses?: number
  funding_source?: string
  market_demand?: number
  competition_level?: string
  employee_count?: number
  description?: string
}

export interface StartupUpdateInput {
  business_name?: string
  business_category?: string
  business_model?: string
  investment_amount?: number
  preferred_location?: string
  target_customers?: string
  experience_years?: number
  expected_monthly_revenue?: number
  market_demand?: number
  competition_level?: string
  employee_count?: number
  description?: string
}

export interface StartupFilterParams {
  query?: string
  category?: string
  min_investment?: number
  max_investment?: number
  sort_by?: 'newest' | 'oldest' | 'highest_investment' | 'lowest_investment' | 'alphabetical'
  page?: number
  per_page?: number
}

export interface StartupStats {
  total_startups: number
  total_investment: number
  avg_investment: number
  latest_startup_name?: string
  latest_startup_id?: string
  category_breakdown?: Record<string, number>
}
