/**
 * STARTWISE AI — Admin Settings Page (Stage 12)
 * Shows platform configuration. Sensitive secrets are NEVER displayed.
 */

import { RefreshCw, CheckCircle2, XCircle, AlertTriangle, Lock } from 'lucide-react'
import { useAdminSettings } from '@/hooks/useAdmin'

function SettingRow({ label, value, status }: { label: string; value: string | boolean | number; status?: 'ok' | 'warn' | 'error' }) {
  const display = typeof value === 'boolean' ? (value ? '✓ Enabled' : '✗ Disabled') : String(value)
  return (
    <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-0 gap-4">
      <span className="text-sm text-slate-400">{label}</span>
      <div className="flex items-center gap-2">
        {status === 'ok' && <CheckCircle2 className="h-4 w-4 text-green-400 flex-shrink-0" />}
        {status === 'warn' && <AlertTriangle className="h-4 w-4 text-amber-400 flex-shrink-0" />}
        {status === 'error' && <XCircle className="h-4 w-4 text-red-400 flex-shrink-0" />}
        <span className={`text-sm font-semibold ${
          status === 'ok' ? 'text-green-400' :
          status === 'warn' ? 'text-amber-400' :
          status === 'error' ? 'text-red-400' :
          'text-white'
        }`}>{display}</span>
      </div>
    </div>
  )
}

function SettingsSection({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="bg-slate-900 border border-white/10 rounded-2xl overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10 bg-slate-800/50">
        {icon}
        <h3 className="text-sm font-bold text-white">{title}</h3>
      </div>
      <div className="px-5 py-2">
        {children}
      </div>
    </div>
  )
}

export default function AdminSettingsPage() {
  const { data, isLoading, refetch, isFetching } = useAdminSettings()
  const settings = data as any

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white">Platform Settings</h1>
          <p className="text-sm text-slate-400 mt-1">Read-only overview of platform configuration.</p>
        </div>
        <button onClick={() => refetch()} disabled={isFetching} className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-white/10 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-700 transition-colors">
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* Security Notice */}
      <div className="flex items-center gap-3 px-4 py-3 bg-slate-800/60 border border-white/10 rounded-xl">
        <Lock className="h-4 w-4 text-slate-500 flex-shrink-0" />
        <p className="text-xs text-slate-400">
          Sensitive values such as <strong className="text-slate-300">JWT_SECRET</strong>, <strong className="text-slate-300">DATABASE_URL</strong>, and <strong className="text-slate-300">RESEND_API_KEY</strong> are never displayed here for security reasons.
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-slate-900 border border-white/10 rounded-2xl p-6 animate-pulse space-y-4">
              <div className="h-4 bg-slate-800 rounded w-32" />
              {Array.from({ length: 4 }).map((_, j) => <div key={j} className="h-3 bg-slate-800 rounded w-full" />)}
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Platform */}
          <SettingsSection title="Platform" icon={<div className="h-4 w-4 rounded-full bg-gradient-to-br from-cyan-500 to-indigo-600" />}>
            <SettingRow label="App Name" value={settings?.platform?.name || '—'} />
            <SettingRow label="Version" value={settings?.platform?.version || '—'} />
            <SettingRow label="Environment" value={settings?.platform?.environment || '—'} status={settings?.platform?.environment === 'production' ? 'ok' : 'warn'} />
            <SettingRow label="Debug Mode" value={settings?.platform?.debug_mode} status={settings?.platform?.debug_mode ? 'warn' : 'ok'} />
          </SettingsSection>

          {/* Email */}
          <SettingsSection title="Email (Resend)" icon={<div className="h-4 w-4 rounded-full bg-gradient-to-br from-violet-500 to-purple-600" />}>
            <SettingRow label="Provider" value={settings?.email?.provider || '—'} />
            <SettingRow label="API Key Status" value={settings?.email?.api_key_status || '—'} status={settings?.email?.api_key_status === 'Configured' ? 'ok' : 'error'} />
            <SettingRow label="From Name" value={settings?.email?.from_name || '—'} />
            <SettingRow label="From Address" value={settings?.email?.from_address || '—'} />
          </SettingsSection>

          {/* ML */}
          <SettingsSection title="ML Engine" icon={<div className="h-4 w-4 rounded-full bg-gradient-to-br from-green-500 to-emerald-600" />}>
            <SettingRow label="Model Version" value={settings?.ml?.model_version || '—'} />
            <SettingRow label="Models Loaded" value={settings?.ml?.models_loaded ? 'Yes' : 'No'} status={settings?.ml?.models_loaded ? 'ok' : 'error'} />
            <SettingRow label="Model Health" value={settings?.ml?.model_health || '—'} status={settings?.ml?.model_health === 'healthy' ? 'ok' : 'warn'} />
            <SettingRow label="Retraining" value={settings?.ml?.retraining || '—'} />
            <div className="py-3">
              <p className="text-xs text-slate-500 font-mono truncate">📂 {settings?.ml?.artifacts_dir}</p>
            </div>
          </SettingsSection>

          {/* Security */}
          <SettingsSection title="Security" icon={<div className="h-4 w-4 rounded-full bg-gradient-to-br from-amber-500 to-orange-600" />}>
            <SettingRow label="JWT Configured" value={settings?.security?.jwt_configured ? 'Yes' : 'No'} status={settings?.security?.jwt_configured ? 'ok' : 'error'} />
            <SettingRow label="Database Configured" value={settings?.security?.database_configured ? 'Yes' : 'No'} status={settings?.security?.database_configured ? 'ok' : 'error'} />
            <SettingRow label="Rate Limiting" value={settings?.security?.rate_limiting || '—'} status="ok" />
            <SettingRow label="JWT Secret" value="••••••••••••••••••••••••••••••••" />
            <SettingRow label="Database URL" value="••••••••••••••••••••••••••••••••" />
          </SettingsSection>
        </div>
      )}
    </div>
  )
}
