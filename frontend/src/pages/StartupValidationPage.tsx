/**
 * STARTWISE AI — Startup Validation Page Component (Stage 7)
 * Interactive form for submitting startup parameters and triggering live ML predictions.
 */

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { BrainCircuit, Sparkles, Building2, MapPin, DollarSign, Users, Award } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { GlassCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { PredictionResultsView } from '@/components/dashboard/PredictionResultsView'
import { useAnalyzeStartup } from '@/hooks/usePredictions'
import { PredictionAnalysisResponse } from '@/types/prediction'

const validationSchema = z.object({
  business_name: z.string().min(2, 'Business name must be at least 2 characters'),
  business_category: z.string().min(1, 'Please select a category'),
  business_model: z.string().min(1, 'Business model is required'),
  investment_amount: z.coerce.number().gt(0, 'Investment amount must be greater than 0'),
  preferred_location: z.string().min(2, 'Location is required'),
  target_customers: z.string().min(2, 'Target customer demographic is required'),
  experience_years: z.coerce.number().min(0, 'Experience years required'),
  expected_monthly_revenue: z.coerce.number().min(0, 'Expected revenue required'),
  expected_monthly_expenses: z.coerce.number().min(0, 'Expected expenses required'),
  employee_count: z.coerce.number().min(0, 'Employee count required'),
  description: z.string().optional(),
})

type ValidationForm = z.infer<typeof validationSchema>

export default function StartupValidationPage() {
  const [prediction, setPrediction] = useState<PredictionAnalysisResponse | null>(null)
  const analyzeMutation = useAnalyzeStartup()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ValidationForm>({
    resolver: zodResolver(validationSchema),
    defaultValues: {
      business_name: 'Urban Brew Lounge',
      business_category: 'Food',
      business_model: 'Cafe',
      investment_amount: 800000,
      preferred_location: 'Bengaluru',
      target_customers: 'Young professionals & students',
      experience_years: 3,
      expected_monthly_revenue: 250000,
      expected_monthly_expenses: 150000,
      employee_count: 5,
      description: 'Specialty coffee workspace with high-speed internet and private meeting pods.',
    },
  })

  const onSubmit = (data: ValidationForm) => {
    setPrediction(null)
    analyzeMutation.mutate(
      {
        business_name: data.business_name,
        business_category: data.business_category,
        business_model: data.business_model,
        business_description: data.description,
        investment_amount: data.investment_amount,
        expected_monthly_revenue: data.expected_monthly_revenue,
        expected_monthly_expenses: data.expected_monthly_expenses,
        employee_count: data.employee_count,
        experience_years: data.experience_years,
        location: data.preferred_location,
        target_customer: data.target_customers,
        market_demand: 8,
        competition_level: 'Medium',
        funding_source: 'Personal',
      },
      {
        onSuccess: (res) => {
          setPrediction(res)
        },
      }
    )
  }

  return (
    <div className="space-y-8 pb-12">
      <Breadcrumb items={[{ label: 'AI Startup Validation' }]} />

      {/* Header Banner */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
          <BrainCircuit className="h-4 w-4" /> Live Machine Learning Feasibility Engine
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
          Validate Your Business Idea
        </h1>
        <p className="text-sm text-slate-500 dark:text-zinc-400 max-w-2xl">
          Enter your financial parameters and business concept to run inference across 4 trained Machine Learning models.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form Container */}
        <GlassCard className="lg:col-span-5 p-6 sm:p-8 space-y-6">
          <div className="flex items-center gap-3 border-b border-slate-200/80 dark:border-zinc-800 pb-4">
            <div className="h-10 w-10 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center font-bold">
              1
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Business Parameters</h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400">Fill in your startup concept details</p>
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            <Input
              label="Business Name"
              type="text"
              placeholder="e.g. Urban Brew Lounge"
              leftIcon={<Building2 className="h-4 w-4 text-slate-400" />}
              error={errors.business_name?.message}
              required
              {...register('business_name')}
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Select
                label="Business Category"
                options={[
                  { label: 'Food & Beverage', value: 'Food' },
                  { label: 'Retail & E-Commerce', value: 'Retail' },
                  { label: 'Technology & Software', value: 'Technology' },
                  { label: 'Healthcare & Pharma', value: 'Healthcare' },
                  { label: 'Education & Training', value: 'Education' },
                  { label: 'Services & Salon', value: 'Services' },
                  { label: 'Manufacturing', value: 'Manufacturing' },
                  { label: 'Finance & Fintech', value: 'Finance' },
                ]}
                error={errors.business_category?.message}
                {...register('business_category')}
              />

              <Input
                label="Business Model"
                type="text"
                placeholder="e.g. Cafe, SaaS, Clinic"
                error={errors.business_model?.message}
                {...register('business_model')}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Capital Investment (₹)"
                type="number"
                placeholder="800000"
                leftIcon={<DollarSign className="h-4 w-4 text-slate-400" />}
                error={errors.investment_amount?.message}
                required
                {...register('investment_amount')}
              />

              <Input
                label="Target City / Location"
                type="text"
                placeholder="e.g. Bengaluru"
                leftIcon={<MapPin className="h-4 w-4 text-slate-400" />}
                error={errors.preferred_location?.message}
                required
                {...register('preferred_location')}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Est. Monthly Revenue (₹)"
                type="number"
                placeholder="250000"
                error={errors.expected_monthly_revenue?.message}
                {...register('expected_monthly_revenue')}
              />

              <Input
                label="Est. Monthly Expenses (₹)"
                type="number"
                placeholder="150000"
                error={errors.expected_monthly_expenses?.message}
                {...register('expected_monthly_expenses')}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Input
                label="Target Segment"
                type="text"
                placeholder="Students"
                error={errors.target_customers?.message}
                {...register('target_customers')}
              />

              <Input
                label="Experience (Yrs)"
                type="number"
                placeholder="3"
                leftIcon={<Award className="h-4 w-4 text-slate-400" />}
                error={errors.experience_years?.message}
                {...register('experience_years')}
              />

              <Input
                label="Team Members"
                type="number"
                placeholder="5"
                leftIcon={<Users className="h-4 w-4 text-slate-400" />}
                error={errors.employee_count?.message}
                {...register('employee_count')}
              />
            </div>

            <Textarea
              label="Business Concept USP"
              placeholder="Describe your unique value proposition..."
              rows={2}
              {...register('description')}
            />

            <Button
              type="submit"
              size="lg"
              isLoading={analyzeMutation.isPending}
              rightIcon={!analyzeMutation.isPending ? <Sparkles className="h-5 w-5" /> : undefined}
              className="w-full bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-2xl py-4 shadow-xl shadow-cyan-500/20"
            >
              {analyzeMutation.isPending ? 'Running Machine Learning Inference...' : 'Run Live ML Validation'}
            </Button>
          </form>
        </GlassCard>

        {/* Results Container */}
        <div className="lg:col-span-7 space-y-6">
          <AnimatePresence mode="wait">
            {analyzeMutation.isPending ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
              >
                <GlassCard className="p-12 text-center space-y-6 border border-cyan-500/30">
                  <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
                    <div className="absolute inset-0 rounded-full border-4 border-cyan-500/20 border-t-cyan-500 animate-spin" />
                    <BrainCircuit className="h-10 w-10 text-cyan-500 animate-pulse" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-xl font-black text-slate-900 dark:text-white">
                      Loading AI Analysis...
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-zinc-400 max-w-sm mx-auto">
                      Preprocessing feature vectors, executing RandomForestClassifier & DecisionTree models, and computing Business Score...
                    </p>
                  </div>
                </GlassCard>
              </motion.div>
            ) : prediction ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <PredictionResultsView
                  prediction={prediction}
                  onReanalyzeSuccess={(updated) => setPrediction(updated)}
                />
              </motion.div>
            ) : (
              <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <GlassCard className="p-12 text-center space-y-4 text-slate-500 dark:text-zinc-400 border-dashed border-2">
                  <div className="h-16 w-16 rounded-3xl bg-cyan-500/10 text-cyan-500 flex items-center justify-center mx-auto shadow-sm">
                    <BrainCircuit className="h-8 w-8" />
                  </div>
                  <h4 className="text-xl font-bold text-slate-900 dark:text-white">AI Engine Standby</h4>
                  <p className="text-xs leading-relaxed max-w-md mx-auto">
                    Fill in your business financial parameters on the left and click <strong>"Run Live ML Validation"</strong> to trigger real-time model inference.
                  </p>
                </GlassCard>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
