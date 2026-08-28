/**
 * STARTWISE AI — Marketing Strategy Types (Stage 9)
 */

export interface SubScores {
  category_fit: number
  target_audience_fit: number
  budget_fit: number
  business_model_fit: number
  location_fit: number
  competition_fit: number
  demand_fit: number
  time_to_results_fit: number
}

export interface MarketingChannelItem {
  channel_name: string
  platform: string
  target_audience: string[]
  business_categories: string[]
  minimum_budget: number
  recommended_budget: number
  cost_level: 'Low' | 'Medium' | 'High' | string
  reach_level: 'Local' | 'Regional' | 'National' | 'Global' | string
  conversion_potential: 'High' | 'Medium' | 'Moderate' | string
  local_business_score: number
  digital_score: number
  b2b_score: number
  b2c_score: number
  difficulty: 'Easy' | 'Moderate' | 'Advanced' | string
  time_to_results: string
  description: string
  best_for: string
  marketing_score: number
  score_label: string
  ranking_position: number
  allocated_budget: number
  explanation: string[]
  sub_scores: SubScores
}

export interface CampaignIdeaItem {
  campaign_name: string
  platform: string
  objective: string
  target_audience: string
  estimated_budget: number
  call_to_action: string
  description: string
}

export interface ThirtyDayTaskItem {
  task_name: string
  channel: string
  expected_objective: string
  kpis: string
  status: 'Pending' | 'Completed' | string
}

export interface ThirtyDayWeekPhase {
  week: number
  phase: string
  tasks: ThirtyDayTaskItem[]
}

export interface BudgetScenarioDetails {
  label: string
  total: number
  description: string
  allocation: Record<string, number>
}

export interface BudgetAllocationData {
  recommended_total: number
  scenarios: {
    LOW_BUDGET: BudgetScenarioDetails
    BALANCED: BudgetScenarioDetails
    AGGRESSIVE: BudgetScenarioDetails
  }
}

export interface ContentStrategyData {
  content_pillars: string[]
  social_media_posts: string[]
  reels_and_shorts: string[]
  blog_ideas: string[]
  email_templates: string[]
  whatsapp_messages: string[]
  call_to_actions: string[]
}

export interface KPIMetricItem {
  metric: string
  target: string
  category: string
}

export interface MarketingStrategyResponse {
  id?: string
  startup_id: string
  user_id?: string
  strategy_name: string
  strategy_type: 'LOW_BUDGET' | 'BALANCED' | 'AGGRESSIVE' | string
  marketing_score: number
  strategy_label: string
  total_recommended_budget: number
  profile: Record<string, any>
  recommended_channels: MarketingChannelItem[]
  budget_allocation: BudgetAllocationData
  campaign_ideas: CampaignIdeaItem[]
  content_strategy: ContentStrategyData
  thirty_day_plan: ThirtyDayWeekPhase[]
  kpis: KPIMetricItem[]
  disclaimer?: string
  created_at?: string
}

export interface MarketingStrategyRequest {
  startup_id: string
}
