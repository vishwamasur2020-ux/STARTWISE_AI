/**
 * STARTWISE AI — Feature Impact Chart (Stage 13 XAI)
 * Horizontal divergence bar chart rendering exact SHAP attributions
 * with positive (+ emerald/teal) and negative (- rose/amber) indicators.
 */

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ReferenceLine,
} from 'recharts'
import type { FeatureImpactItem } from '@/types/explainability'

interface FeatureImpactChartProps {
  features: FeatureImpactItem[]
  maxItems?: number
  height?: number
}

export function FeatureImpactChart({
  features,
  maxItems = 8,
  height = 280,
}: FeatureImpactChartProps) {
  const chartData = features
    .slice(0, maxItems)
    .map((f) => ({
      name: f.display_name.length > 24 ? f.display_name.slice(0, 22) + '…' : f.display_name,
      fullName: f.display_name,
      impact: f.impact_value,
      direction: f.direction,
      userValue: f.user_value !== undefined && f.user_value !== null ? String(f.user_value) : '—',
      description: f.description,
    }))
    .reverse() // Reverse so highest importance appears on top

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
        >
          <XAxis
            type="number"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            tickLine={false}
            tickFormatter={(val) => `${val > 0 ? '+' : ''}${val.toFixed(2)}`}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: '#cbd5e1', fontSize: 11, fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
            width={140}
          />
          <ReferenceLine x={0} stroke="rgba(255,255,255,0.2)" strokeDasharray="3 3" />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload
                const isPos = data.impact >= 0
                return (
                  <div className="bg-slate-900/95 border border-white/15 p-3 rounded-xl shadow-2xl backdrop-blur-md max-w-xs text-xs space-y-1.5 z-50">
                    <p className="font-bold text-white text-sm">{data.fullName}</p>
                    <div className="flex items-center justify-between gap-4 text-slate-300">
                      <span>Model Impact:</span>
                      <span
                        className={`font-mono font-bold ${
                          isPos ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {isPos ? '+' : ''}
                        {data.impact.toFixed(4)}
                      </span>
                    </div>
                    {data.userValue && (
                      <div className="flex items-center justify-between gap-4 text-slate-400">
                        <span>Input Value:</span>
                        <span className="font-semibold text-slate-200">{data.userValue}</span>
                      </div>
                    )}
                    <p className="text-slate-400 text-[11px] leading-relaxed pt-1 border-t border-white/10">
                      {data.description}
                    </p>
                  </div>
                )
              }
              return null
            }}
          />
          <Bar dataKey="impact" radius={[4, 4, 4, 4]} barSize={16}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  entry.impact >= 0
                    ? '#10b981' // Emerald for positive contribution
                    : '#f43f5e' // Rose for negative contribution
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
