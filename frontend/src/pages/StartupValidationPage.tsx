/**
 * STARTWISE AI — Startup Validation Page Component
 * Interactive wizard form for submitting startup parameters and previewing AI prediction scoring.
 */

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { BrainCircuit, Sparkles, CheckCircle2, Building2, MapPin, DollarSign, Users, Award } from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { GlassCard, AIResultCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'

const validationSchema = z.object({
  business_name: z.string().min(2, 'Business name is required'),
  business_category: z.string().min(1, 'Please select a category'),
  investment_amount: z.coerce.number().gt(0, 'Investment amount must be greater than 0'),
  preferred_location: z.string().min(2, 'Location is required'),
  target_customers: z.string().min(2, 'Target customer demographic is required'),
  experience_years: z.coerce.number().min(0, 'Experience years required'),
  expected_monthly_revenue: z.coerce.number().min(0, 'Expected revenue required'),
  description: z.string().optional(),
})

type ValidationForm = z.infer<typeof validationSchema>

export default function StartupValidationPage() {
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<any | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ValidationForm>({
    resolver: zodResolver(validationSchema),
    defaultValues: {
      business_name: 'Urban Brew Coffee & Workstation',
      business_category: 'Food',
      investment_amount: 1500000,
      preferred_location: 'Indiranagar, Bengaluru',
      target_customers: 'Remote tech professionals & students',
      experience_years: 4,
      expected_monthly_revenue: 350000,
      description: 'Specialty coffee lounge with high-speed Wi-Fi and quiet co-working booths.',
    },
  })

  const onSubmit = (_data: ValidationForm) => {
    setAnalyzing(true)
    setResult(null)

    // Simulate AI prediction calculations
    setTimeout(() => {
      setAnalyzing(false)
      setResult({
        score: 91.5,
        riskLevel: 'Low',
        estimatedRoi: 38.4,
        confidenceScore: 94.2,
        recommendations: [
          'High demand location: Bengaluru commercial hubs show 4.2x coffee cup consumption.',
          'Suggested price point: ₹180 - ₹240 per specialty brew for 68% gross margin.',
          'Consider adding quick grab-and-go breakfast combos for morning rush hour.',
        ],
        matchedFranchise: 'Tea Time or Amul Scoop Parlour as alternative lower-cap model',
      })
      toast.success('AI Startup Feasibility Analysis Complete! 🚀')
    }, 1500)
  }

  return (
    <div className="space-y-8 pb-12">
      <Breadcrumb items={[{ label: 'AI Startup Validation' }]} />

      {/* Header Banner */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
          <BrainCircuit className="h-4 w-4" /> Machine Learning Feasibility Engine
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
          Validate Your Business Idea
        </h1>
        <p className="text-sm text-slate-500 dark:text-zinc-400 max-w-2xl">
          Enter your financial budget and business parameters to receive a instant ML success score, ROI prediction, and risk profile.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Container */}
        <GlassCard className="lg:col-span-2 p-6 sm:p-8 space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-200/80 dark:border-zinc-800 pb-4">
            <div className="h-10 w-10 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center font-bold">
              1
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Business Parameters</h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400">Fill in your startup concept details</p>
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <Input
                label="Business Name"
                type="text"
                placeholder="e.g. Urban Brew Lounge"
                leftIcon={<Building2 className="h-4 w-4 text-slate-400" />}
                error={errors.business_name?.message}
                required
                {...register('business_name')}
              />

              <Select
                label="Business Category"
                options={[
                  { label: 'Food & Beverage', value: 'Food' },
                  { label: 'Retail & E-Commerce', value: 'Retail' },
                  { label: 'Technology & Software', value: 'Technology' },
                  { label: 'Healthcare & Pharma', value: 'Healthcare' },
                  { label: 'Education & Training', value: 'Education' },
                  { label: 'Services & Salon', value: 'Services' },
                ]}
                error={errors.business_category?.message}
                {...register('business_category')}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <Input
                label="Capital Investment (₹ INR)"
                type="number"
                placeholder="1500000"
                leftIcon={<DollarSign className="h-4 w-4 text-slate-400" />}
                error={errors.investment_amount?.message}
                required
                {...register('investment_amount')}
              />

              <Input
                label="Target Location / City"
                type="text"
                placeholder="e.g. Indiranagar, Bengaluru"
                leftIcon={<MapPin className="h-4 w-4 text-slate-400" />}
                error={errors.preferred_location?.message}
                required
                {...register('preferred_location')}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <Input
                label="Target Customer Segment"
                type="text"
                placeholder="e.g. Young professionals & students"
                leftIcon={<Users className="h-4 w-4 text-slate-400" />}
                error={errors.target_customers?.message}
                required
                {...register('target_customers')}
              />

              <Input
                label="Team Experience (Years)"
                type="number"
                placeholder="4"
                leftIcon={<Award className="h-4 w-4 text-slate-400" />}
                error={errors.experience_years?.message}
                {...register('experience_years')}
              />
            </div>

            <Textarea
              label="Business Description & Unique Selling Point (USP)"
              placeholder="Describe your product/service offerings, pricing strategy, and competitive edge..."
              rows={3}
              {...register('description')}
            />

            <Button
              type="submit"
              size="lg"
              isLoading={analyzing}
              rightIcon={<Sparkles className="h-5 w-5" />}
              className="w-full bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-2xl py-4 shadow-xl shadow-cyan-500/20"
            >
              {analyzing ? 'Analyzing Market Data...' : 'Run AI Feasibility Validation'}
            </Button>
          </form>
        </GlassCard>

        {/* Prediction Results Preview */}
        <div className="space-y-6">
          {result ? (
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <AIResultCard
                score={result.score}
                riskLevel={result.riskLevel}
                estimatedRoi={result.estimatedRoi}
                summary="High viability score backed by strong regional footfall and favorable profit margins."
              />

              <GlassCard className="p-6 space-y-4">
                <h4 className="font-bold text-slate-900 dark:text-white text-sm">Strategic Recommendations</h4>
                <ul className="space-y-2.5 text-xs text-slate-600 dark:text-zinc-300">
                  {result.recommendations.map((rec: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </GlassCard>
            </motion.div>
          ) : (
            <GlassCard className="p-8 text-center space-y-4 text-slate-500 dark:text-zinc-400">
              <div className="h-16 w-16 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mx-auto shadow-sm">
                <BrainCircuit className="h-8 w-8" />
              </div>
              <h4 className="text-lg font-bold text-slate-900 dark:text-white">AI Engine Ready</h4>
              <p className="text-xs leading-relaxed">
                Fill out the business form on the left and click "Run AI Feasibility Validation" to generate score predictions.
              </p>
            </GlassCard>
          )}
        </div>
      </div>
    </div>
  )
}
