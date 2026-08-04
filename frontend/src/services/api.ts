/**
 * STARTWISE AI — Axios HTTP Client
 * Configured with interceptors for auth token injection and 401 refresh handling.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import toast from 'react-hot-toast'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// ─── Axios Instance ──────────────────────────────────────────────────────────
export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// ─── Token Helpers ───────────────────────────────────────────────────────────
const getAccessToken = () => localStorage.getItem('access_token')
const getRefreshToken = () => localStorage.getItem('refresh_token')
const setTokens = (access: string, refresh: string) => {
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}
const clearTokens = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

// ─── Request Interceptor — Inject Bearer Token ────────────────────────────
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ─── Response Interceptor — Handle 401 with Token Refresh ────────────────
let isRefreshing = false
let pendingQueue: Array<{
  resolve: (token: string) => void
  reject: (err: unknown) => void
}> = []

const flushQueue = (token: string | null, error?: unknown) => {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (token) resolve(token)
    else reject(error)
  })
  pendingQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        const response = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        const { access_token, refresh_token } = response.data
        setTokens(access_token, refresh_token)
        api.defaults.headers.Authorization = `Bearer ${access_token}`
        flushQueue(access_token)
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        flushQueue(null, refreshError)
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Handle other errors
    const detail =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      'Something went wrong'

    // Don't toast for 401 (handled above) or 404 (handled in components)
    if (error.response?.status !== 401 && error.response?.status !== 404) {
      toast.error(detail, { duration: 4000 })
    }

    return Promise.reject(error)
  }
)

export { getAccessToken, getRefreshToken, setTokens, clearTokens }
export default api
