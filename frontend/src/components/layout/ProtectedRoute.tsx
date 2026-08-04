/**
 * STARTWISE AI — Protected Route Guard
 * Enforces authentication and Role Based Access Control (RBAC).
 */

import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { getAccessToken } from '@/services/api'
import toast from 'react-hot-toast'

interface ProtectedRouteProps {
  requiredRole?: 'user' | 'admin' | string
  allowedRoles?: string[]
}

export function ProtectedRoute({ requiredRole, allowedRoles }: ProtectedRouteProps = {}) {
  const { user, isAuthenticated } = useAuthStore()
  const location = useLocation()
  const hasToken = !!getAccessToken()

  if (!isAuthenticated && !hasToken) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check RBAC Role if requiredRole or allowedRoles specified
  const roles = allowedRoles || (requiredRole ? [requiredRole] : [])
  if (roles.length > 0 && user && !roles.includes(user.role)) {
    toast.error(`Access restricted. Admin permissions required.`)
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export function PublicOnlyRoute() {
  const { isAuthenticated } = useAuthStore()
  const hasToken = !!getAccessToken()

  if (isAuthenticated && hasToken) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
