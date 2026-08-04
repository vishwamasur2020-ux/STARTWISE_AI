/**
 * STARTWISE AI — Startup API Service
 * Axios client calls for Stage 5 Startup Validation module (/api/startups).
 */

import api from '@/services/api'
import { StartupIdea, StartupCreateInput, StartupUpdateInput, StartupFilterParams, StartupStats } from '@/types/startup'

export const startupService = {
  /** Create a new startup idea */
  async createStartup(data: StartupCreateInput): Promise<StartupIdea> {
    const res = await api.post<StartupIdea>('/api/startups', data)
    return res.data
  },

  /** List user startup ideas with search, category, investment, sorting, and pagination */
  async getStartups(params?: StartupFilterParams) {
    const res = await api.get('/api/startups', { params })
    return res.data
  },

  /** Retrieve recent startup ideas for dashboard */
  async getRecentStartups(limit = 5): Promise<StartupIdea[]> {
    const res = await api.get<StartupIdea[]>('/api/startups/recent', { params: { limit } })
    return res.data
  },

  /** Retrieve startup dashboard statistics summary */
  async getStartupStats(): Promise<StartupStats> {
    const res = await api.get<StartupStats>('/api/startups/statistics')
    return res.data
  },

  /** Get single startup idea details */
  async getStartupDetails(id: string): Promise<StartupIdea> {
    const res = await api.get<StartupIdea>(`/api/startups/${id}`)
    return res.data
  },

  /** Update an existing startup idea */
  async updateStartup(id: string, data: StartupUpdateInput): Promise<StartupIdea> {
    const res = await api.put<StartupIdea>(`/api/startups/${id}`, data)
    return res.data
  },

  /** Delete a startup idea */
  async deleteStartup(id: string): Promise<{ message: string; success: boolean }> {
    const res = await api.delete<{ message: string; success: boolean }>(`/api/startups/${id}`)
    return res.data
  },
}
