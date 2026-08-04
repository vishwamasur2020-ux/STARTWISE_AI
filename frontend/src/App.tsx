/**
 * STARTWISE AI — App Router (Stage 5 Complete)
 * Defines all application routes including Startup Validation CRUD, history, and details.
 */

import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'react-hot-toast'

import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { ProtectedRoute, PublicOnlyRoute } from '@/components/layout/ProtectedRoute'
import { DashboardSkeleton } from '@/components/ui/Skeleton'
import { useTheme } from '@/hooks/useTheme'

// ── Lazy Loaded Pages ───────────────────────────────────────────────────────────
const LandingPage           = lazy(() => import('@/pages/LandingPage'))
const LoginPage             = lazy(() => import('@/pages/LoginPage'))
const RegisterPage          = lazy(() => import('@/pages/RegisterPage'))
const ForgotPasswordPage    = lazy(() => import('@/pages/ForgotPasswordPage'))
const ResetPasswordPage     = lazy(() => import('@/pages/ResetPasswordPage'))
const ProfilePage           = lazy(() => import('@/pages/ProfilePage'))
const DashboardPage         = lazy(() => import('@/pages/DashboardPage'))
const StartupValidationPage = lazy(() => import('@/pages/StartupValidationPage'))
const CreateStartupPage     = lazy(() => import('@/pages/CreateStartupPage'))
const EditStartupPage       = lazy(() => import('@/pages/EditStartupPage'))
const StartupDetailsPage    = lazy(() => import('@/pages/StartupDetailsPage'))
const StartupHistoryPage    = lazy(() => import('@/pages/StartupHistoryPage'))
const FranchisePage         = lazy(() => import('@/pages/FranchisePage'))
const ReportsPage           = lazy(() => import('@/pages/ReportsPage'))
const AdminDashboardPage    = lazy(() => import('@/pages/AdminDashboardPage'))
const NotFoundPage          = lazy(() => import('@/pages/NotFoundPage'))

// ── Query Client Config ───────────────────────────────────────────────────────
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 2 * 60 * 1000,
      gcTime: 5 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
})

// ── Loading Fallback Component ──────────────────────────────────────────────
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center animated-bg">
    <div className="page-container w-full max-w-4xl">
      <DashboardSkeleton />
    </div>
  </div>
)

// ── Theme Provider Wrapper ──────────────────────────────────────────────────
function ThemeProvider({ children }: { children: React.ReactNode }) {
  useTheme()
  return <>{children}</>
}

// ── App Main Router ─────────────────────────────────────────────────────────
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Public Landing */}
              <Route path="/" element={<LandingPage />} />

              {/* Public Auth Routes */}
              <Route element={<PublicOnlyRoute />}>
                <Route path="/login"           element={<LoginPage />} />
                <Route path="/register"        element={<RegisterPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password"  element={<ResetPasswordPage />} />
              </Route>

              {/* Protected Dashboard App Routes */}
              <Route element={<ProtectedRoute />}>
                <Route element={<DashboardLayout />}>
                  <Route path="/dashboard"                   element={<DashboardPage />} />
                  <Route path="/startup-validation"          element={<StartupValidationPage />} />
                  <Route path="/startup-validation/new"      element={<CreateStartupPage />} />
                  <Route path="/startup-validation/edit/:id" element={<EditStartupPage />} />
                  <Route path="/startup-validation/history text-sans"  element={<StartupHistoryPage />} />
                  <Route path="/startup-validation/history font-sans" element={<StartupHistoryPage />} />
                  <Route path="/startup-validation/history" element={<StartupHistoryPage />} />
                  <Route path="/startup-validation/:id"      element={<StartupDetailsPage />} />
                  <Route path="/validate"                    element={<StartupValidationPage />} />
                  <Route path="/franchise"                   element={<FranchisePage />} />
                  <Route path="/franchises"                  element={<FranchisePage />} />
                  <Route path="/reports"                     element={<ReportsPage />} />
                  <Route path="/profile"                     element={<ProfilePage />} />
                  <Route path="/settings font-sans"          element={<ProfilePage />} />
                  <Route path="/settings"                    element={<ProfilePage />} />

                  {/* Admin Only Route Guard */}
                  <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
                    <Route path="/admin" element={<AdminDashboardPage />} />
                  </Route>
                </Route>
              </Route>

              {/* 404 Catch All */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </BrowserRouter>

        {/* Global Toast Notifications */}
        <Toaster
          position="top-right"
          gutter={8}
          toastOptions={{
            duration: 4000,
            style: {
              borderRadius: '16px',
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              backdropFilter: 'blur(16px)',
              boxShadow: '0 10px 30px rgba(0,0,0,0.12)',
              fontSize: '14px',
              fontWeight: 600,
              border: '1px solid rgba(6,182,212,0.2)',
            },
            success: {
              iconTheme: { primary: '#06B6D4', secondary: '#fff' },
            },
            error: {
              iconTheme: { primary: '#F43F5E', secondary: '#fff' },
            },
          }}
        />

        {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
      </ThemeProvider>
    </QueryClientProvider>
  )
}
