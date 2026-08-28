/**
 * STARTWISE AI — Marketing API Service (Stage 9)
 * Client calls for AI Marketing & Promotion Strategy Engine (/api/v1/marketing).
 */

import api from '@/services/api'
import {
  MarketingStrategyResponse,
  MarketingChannelItem,
  ThirtyDayWeekPhase,
  ContentStrategyData,
} from '@/types/marketing'

export const marketingService = {
  /** Generate personalized marketing strategy */
  async analyzeMarketing(startupId: string): Promise<MarketingStrategyResponse> {
    const res = await api.post<MarketingStrategyResponse>('/api/v1/marketing/analyze', {
      startup_id: startupId,
    })
    return res.data
  },

  /** Get latest marketing strategy for startup */
  async getLatestStrategy(startupId: string): Promise<MarketingStrategyResponse> {
    const res = await api.get<MarketingStrategyResponse>(`/api/v1/marketing/${startupId}`)
    return res.data
  },

  /** Regenerate marketing strategy */
  async regenerateStrategy(startupId: string): Promise<MarketingStrategyResponse> {
    const res = await api.post<MarketingStrategyResponse>(`/api/v1/marketing/${startupId}/regenerate`)
    return res.data
  },

  /** Get top recommended channels only */
  async getChannels(startupId: string): Promise<MarketingChannelItem[]> {
    const res = await api.get<MarketingChannelItem[]>(`/api/v1/marketing/${startupId}/channels`)
    return res.data
  },

  /** Get 30-day plan timeline */
  async getPlan(startupId: string): Promise<ThirtyDayWeekPhase[]> {
    const res = await api.get<ThirtyDayWeekPhase[]>(`/api/v1/marketing/${startupId}/plan`)
    return res.data
  },

  /** Get content strategy ideas */
  async getContent(startupId: string): Promise<ContentStrategyData> {
    const res = await api.get<ContentStrategyData>(`/api/v1/marketing/${startupId}/content`)
    return res.data
  },
}
