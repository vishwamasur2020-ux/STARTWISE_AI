/**
 * STARTWISE AI — Form Wizard Stepper Component
 * Visual step tracker with progress percentage indicator.
 */

import { Check } from 'lucide-react'

export interface Step {
  id: number
  title: string
  subtitle?: string
}

export interface StepperProps {
  steps: Step[]
  currentStep: number
  onStepClick?: (stepId: number) => void
}

export function Stepper({ steps, currentStep, onStepClick }: StepperProps) {
  const progressPercent = Math.round(((currentStep - 1) / (steps.length - 1)) * 100)

  return (
    <div className="w-full space-y-4">
      {/* Progress Line Bar */}
      <div className="relative h-2 w-full bg-slate-100 dark:bg-zinc-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 transition-all duration-500 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Steps Indicator Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {steps.map((step) => {
          const isCompleted = currentStep > step.id
          const isCurrent = currentStep === step.id

          return (
            <button
              key={step.id}
              onClick={() => isCompleted && onStepClick && onStepClick(step.id)}
              disabled={!isCompleted}
              className={`flex items-center gap-3 p-3 rounded-2xl border text-left transition-all ${
                isCurrent
                  ? 'bg-cyan-50/80 dark:bg-cyan-950/40 border-cyan-500 ring-1 ring-cyan-500/20'
                  : isCompleted
                  ? 'bg-white/60 dark:bg-zinc-900/60 border-slate-200 dark:border-zinc-800 hover:border-cyan-300 cursor-pointer'
                  : 'bg-slate-50/50 dark:bg-zinc-900/20 border-slate-100 dark:border-zinc-800/40 opacity-60 cursor-not-allowed'
              }`}
            >
              <div
                className={`h-7 w-7 rounded-xl flex items-center justify-center font-bold text-xs flex-shrink-0 transition-colors ${
                  isCompleted
                    ? 'bg-emerald-500 text-white'
                    : isCurrent
                    ? 'bg-gradient-to-br from-cyan-500 to-indigo-600 text-white shadow-sm'
                    : 'bg-slate-200 dark:bg-zinc-800 text-slate-500'
                }`}
              >
                {isCompleted ? <Check className="h-4 w-4" /> : step.id}
              </div>

              <div className="min-w-0">
                <p className={`text-xs font-bold truncate ${isCurrent ? 'text-cyan-700 dark:text-cyan-300' : 'text-slate-900 dark:text-white'}`}>
                  {step.title}
                </p>
                {step.subtitle && (
                  <p className="text-[10px] text-slate-400 dark:text-zinc-500 truncate hidden sm:block">
                    {step.subtitle}
                  </p>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
