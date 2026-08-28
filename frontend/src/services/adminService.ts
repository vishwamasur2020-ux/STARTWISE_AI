/**
 * STARTWISE AI — Admin API Service (Stage 12)
 * Axios calls to all /api/v1/admin/* endpoints.
 */

import api from './api'

const BASE = '/api/v1/admin'

// ── Dashboard ──────────────────────────────────────────────────────────────
export const adminService = {
  getDashboard: () => api.get(`${BASE}/dashboard`).then(r => r.data),

  // ── Users ────────────────────────────────────────────────────────────────
  getUsers: (params: {
    page?: number
    per_page?: number
    search?: string
    role?: string
    is_active?: boolean
    is_verified?: boolean
  }) => api.get(`${BASE}/users`, { params }).then(r => r.data),

  getUser: (id: string) => api.get(`${BASE}/users/${id}`).then(r => r.data),

  updateUserStatus: (id: string, is_active: boolean) =>
    api.patch(`${BASE}/users/${id}/status`, { is_active }).then(r => r.data),

  updateUserRole: (id: string, role: string) =>
    api.patch(`${BASE}/users/${id}/role`, { role }).then(r => r.data),

  deleteUser: (id: string) =>
    api.delete(`${BASE}/users/${id}`).then(r => r.data),

  // ── Startups ─────────────────────────────────────────────────────────────
  getStartups: (params: {
    page?: number
    per_page?: number
    search?: string
    category?: string
    risk_level?: string
  }) => api.get(`${BASE}/startups`, { params }).then(r => r.data),

  getStartup: (id: string) => api.get(`${BASE}/startups/${id}`).then(r => r.data),

  // ── Predictions ──────────────────────────────────────────────────────────
  getPredictions: (params: {
    page?: number
    per_page?: number
    search?: string
  }) => api.get(`${BASE}/predictions`, { params }).then(r => r.data),

  // ── Franchises ───────────────────────────────────────────────────────────
  getFranchises: (params: {
    page?: number
    per_page?: number
    search?: string
    is_active?: boolean
    industry?: string
  }) => api.get(`${BASE}/franchises`, { params }).then(r => r.data),

  getFranchise: (id: string) => api.get(`${BASE}/franchises/${id}`).then(r => r.data),

  createFranchise: (data: Record<string, unknown>) =>
    api.post(`${BASE}/franchises`, data).then(r => r.data),

  updateFranchise: (id: string, data: Record<string, unknown>) =>
    api.put(`${BASE}/franchises/${id}`, data).then(r => r.data),

  deleteFranchise: (id: string) =>
    api.delete(`${BASE}/franchises/${id}`).then(r => r.data),

  toggleFranchiseStatus: (id: string, is_active: boolean) =>
    api.patch(`${BASE}/franchises/${id}/status`, { is_active }).then(r => r.data),

  // ── Marketing ────────────────────────────────────────────────────────────
  getMarketing: (params: {
    page?: number
    per_page?: number
    search?: string
  }) => api.get(`${BASE}/marketing`, { params }).then(r => r.data),

  deleteMarketing: (id: string) =>
    api.delete(`${BASE}/marketing/${id}`).then(r => r.data),

  // ── Reports ──────────────────────────────────────────────────────────────
  getReports: (params: {
    page?: number
    per_page?: number
    search?: string
  }) => api.get(`${BASE}/reports`, { params }).then(r => r.data),

  deleteReport: (id: string) =>
    api.delete(`${BASE}/reports/${id}`).then(r => r.data),

  // ── ML ───────────────────────────────────────────────────────────────────
  getML: () => api.get(`${BASE}/ml`).then(r => r.data),

  // ── Audit Logs ───────────────────────────────────────────────────────────
  getAuditLogs: (params: {
    page?: number
    per_page?: number
    action?: string
    resource?: string
    start_date?: string
    end_date?: string
  }) => api.get(`${BASE}/audit-logs`, { params }).then(r => r.data),

  // ── Analytics ────────────────────────────────────────────────────────────
  getAnalytics: (params: {
    start_date?: string
    end_date?: string
    group_by?: string
  }) => api.get(`${BASE}/analytics`, { params }).then(r => r.data),

  // ── Settings ─────────────────────────────────────────────────────────────
  getSettings: () => api.get(`${BASE}/settings`).then(r => r.data),
}

export default adminService
