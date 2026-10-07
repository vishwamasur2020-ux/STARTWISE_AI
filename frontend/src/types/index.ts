// ── Auth Types ──────────────────────────────────────────────────────────────
export interface User {
  id: string;
  full_name: string;
  email: string;
  role: 'user' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  email_verified?: boolean;
  email_verified_at?: string | null;
  avatar_url?: string | null;
  profile_image?: string | null;
  phone?: string | null;
  phone_number?: string | null;
  location?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  confirm_password?: string;
  phone_number?: string;
  phone?: string;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
  email: string;
  requires_verification: boolean;
}

export interface VerifyEmailPayload {
  email: string;
  otp: string;
}

export interface ResendOTPPayload {
  email: string;
  purpose?: 'EMAIL_VERIFICATION' | 'PASSWORD_RESET';
}

export interface VerifyResetOTPPayload {
  email: string;
  otp: string;
}

export interface ForgotPasswordPayload {
  email: string;
}

export interface ResetPasswordPayload {
  email?: string;
  otp?: string;
  otp_or_token?: string;
  token?: string;
  new_password: string;
  confirm_password?: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
  confirm_password?: string;
}

export interface VerificationStatus {
  email: string;
  email_verified: boolean;
  email_verified_at?: string | null;
}

export interface UserUpdatePayload {
  full_name?: string;
  phone_number?: string;
  phone?: string;
  location?: string;
  profile_image?: string;
  avatar_url?: string;
}

// ── Business Types ───────────────────────────────────────────────────────────
export interface BusinessIdea {
  id: string;
  user_id: string;
  business_name: string;
  business_category: string;
  investment_amount: number;
  location: string;
  target_customer: string;
  business_experience_years: number;
  monthly_revenue: number;
  market_demand_score: number;
  competition_level: number;
  employees_count: number;
  business_model: string;
  description?: string | null;
  created_at: string;
}

export interface BusinessIdeaCreate {
  business_name: string;
  business_category: string;
  investment_amount: number;
  location: string;
  target_customer: string;
  business_experience_years: number;
  monthly_revenue: number;
  market_demand_score: number;
  competition_level: number;
  employees_count: number;
  business_model: string;
  description?: string;
}

// ── Prediction Types ─────────────────────────────────────────────────────────
export interface PredictionResult {
  id: string;
  business_idea_id: string;
  success_probability: number;    // 0–100
  risk_level: 'Low' | 'Medium' | 'High';
  roi_prediction: number;         // percentage
  competition_score: number;      // 0–100
  business_health_score: number;  // 0–100
  franchise_recommendation: FranchiseRecommendation[] | null;
  marketing_strategy: MarketingChannel[] | null;
  suggestions: string[] | null;
  model_version: string;
  created_at: string;
}

// ── Franchise Types ──────────────────────────────────────────────────────────
export interface Franchise {
  id: string;
  name: string;
  category: string;
  min_investment: number;
  max_investment: number;
  expected_roi: number;
  risk_level: string;
  description?: string;
  advantages: string[];
  disadvantages: string[];
  contact_info: { phone?: string; email?: string; website?: string };
  locations_available: string[];
  logo_url?: string;
  website_url?: string;
  is_active: boolean;
}

export interface FranchiseRecommendation extends Franchise {
  match_score: number;
  reason: string;
}

// ── Marketing Types ──────────────────────────────────────────────────────────
export interface MarketingChannel {
  id: string;
  channel: string;
  strategy_name: string;
  description: string;
  estimated_cost?: string;
  estimated_reach?: string;
  priority: 1 | 2 | 3;
  tips: string[];
}

// ── Report Types ─────────────────────────────────────────────────────────────
export interface Report {
  id: string;
  user_id: string;
  business_idea_id?: string;
  title: string;
  file_path?: string;
  created_at: string;
}

// ── API Generic ──────────────────────────────────────────────────────────────
export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface MessageResponse {
  message: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// ── UI Types ─────────────────────────────────────────────────────────────────
export type RiskLevel = 'Low' | 'Medium' | 'High';
export type Theme = 'light' | 'dark' | 'system';

export interface NavItem {
  label: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  badge?: string;
  children?: NavItem[];
}

export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface DashboardMetrics {
  total_analyses: number;
  avg_success_rate: number;
  avg_roi: number;
  recent_predictions: PredictionResult[];
}
