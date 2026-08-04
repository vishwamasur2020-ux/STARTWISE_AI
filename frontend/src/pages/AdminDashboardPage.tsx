/**
 * STARTWISE AI — Admin Dashboard Page Component
 * Role-Based Access Control portal for user management, system metrics, and audit log monitoring.
 */

import { useState } from 'react'
import { ShieldCheck, Users, Server, Database, UserCheck } from 'lucide-react'

import { GlassCard, StatsCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

const MOCK_USERS = [
  { id: '1', name: 'Vikram Sharma', email: 'vikram@startwise.ai', role: 'admin', status: 'Active', registered: '2026-08-01' },
  { id: '2', name: 'Priya Patel', email: 'priya@example.com', role: 'user', status: 'Active', registered: '2026-08-02' },
  { id: '3', name: 'Rajesh Nair', email: 'rajesh@investor.com', role: 'user', status: 'Active', registered: '2026-08-03' },
  { id: '4', name: 'Ananya Gupta', email: 'ananya@tech.io', role: 'user', status: 'Pending', registered: '2026-08-04' },
]

export default function AdminDashboardPage() {
  const [users] = useState(MOCK_USERS)

  return (
    <div className="space-y-8 pb-12">
      <Breadcrumb items={[{ label: 'Admin Control Center' }]} />

      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-widest">
          <ShieldCheck className="h-4 w-4" /> Role-Based Access Control (RBAC)
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
          System Administration
        </h1>
        <p className="text-sm text-slate-500 dark:text-zinc-400">
          Manage system users, monitor API rate limits, and audit database health metrics.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Registered Users"
          value="1,420"
          change="+12% this week"
          trend="up"
          icon={<Users className="h-5 w-5 text-amber-500" />}
        />
        <StatsCard
          title="Active System Sessions"
          value="342"
          change="Normal Load"
          trend="neutral"
          icon={<UserCheck className="h-5 w-5 text-emerald-500" />}
        />
        <StatsCard
          title="DB Status (Neon Postgres)"
          value="99.99%"
          change="Healthy"
          trend="up"
          icon={<Database className="h-5 w-5 text-cyan-500" />}
        />
        <StatsCard
          title="ML Engine Latency"
          value="140 ms"
          change="Fast"
          trend="up"
          icon={<Server className="h-5 w-5 text-indigo-500" />}
        />
      </div>

      {/* User Management Table */}
      <GlassCard className="p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">User Accounts Directory</h3>
          <Button size="sm" className="bg-amber-500 hover:bg-amber-600 text-white font-semibold text-xs rounded-xl">
            Add New Admin User
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-slate-200 dark:border-zinc-800 text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3 px-4">Name</th>
                <th className="py-3 px-4">Email</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Registered Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-zinc-800">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/50 dark:hover:bg-zinc-800/40">
                  <td className="py-3.5 px-4 font-bold text-slate-900 dark:text-white">{u.name}</td>
                  <td className="py-3.5 px-4 text-slate-500 dark:text-zinc-400">{u.email}</td>
                  <td className="py-3.5 px-4">
                    <Badge variant={u.role === 'admin' ? 'warning' : 'glass'}>
                      {u.role.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2.5 py-0.5 rounded-full font-bold text-[10px] uppercase border ${u.status === 'Active' ? 'bg-emerald-100 text-emerald-700 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-amber-100 text-amber-700 border-amber-300'}`}>
                      {u.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">{u.registered}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  )
}
