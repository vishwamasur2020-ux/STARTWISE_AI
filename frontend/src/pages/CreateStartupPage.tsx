/**
 * STARTWISE AI — Create Startup Validation Wizard
 * 4-step wizard form with Zod inline validation, 30s autosave draft, draft badge, and review summary.
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BrainCircuit,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Building2,
  MapPin,
  DollarSign,
  Users,
  Award,
  CheckCircle2,
  Save,
  Clock,
  Briefcase,
  TrendingUp,
} from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { GlassCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Stepper } from '@/components/ui/Stepper'
import { Badge } from '@/components/ui/Badge'
import { useCreateStartup } from '@/hooks/useStartups'

// ── Zod Form Schema ─────────────────────────────────────────────────────────
const startupWizardSchema = z
  .object({
    // Step 1: Business Info
    business_name: z.string().min(2, 'Business name must be at least 2 characters'),
    business_category: z.string().min(1, 'Please select a business category'),
    business_model: z.string().min(2, 'Business model is required'),
    description: z.string().min(10, 'Description must be at least 10 characters'),

    // Step 2: Financial Info
    investment_amount: z.coerce.number().gt(0, 'Investment amount must be greater than 0'),
    expected_monthly_revenue: z.coerce.number().min(0, 'Expected revenue cannot be negative'),
    expected_expenses: z.coerce.number().min(0, 'Expected expenses cannot be negative'),
    funding_source: z.string().min(1, 'Please select a funding source'),
    employee_count: z.coerce.number().min(1, 'Minimum 1 employee required'),

    // Step 3: Market Info
    target_customers: z.string().min(2, 'Target customer demographic is required'),
    preferred_location: z.string().min(2, 'Preferred location is required'),
    competition_level: z.string().default('Medium'),
    market_demand: z.coerce.number().min(1).max(10).default(5),
    experience_years: z.coerce.number().min(0, 'Experience years cannot be negative'),
  })
  .refine((data) => data.expected_monthly_revenue > data.expected_expenses, {
    message: 'Expected revenue should be greater than monthly expenses for viable profitability.',
    path: ['expected_monthly_revenue'],
  })

type StartupWizardForm = z.infer<typeof startupWizardSchema>

const STEPS = [
  { id: 1, title: 'Business Info', subtitle: 'Name & Model' },
  { id: 2, title: 'Financials', subtitle: 'Capital & Revenue' },
  { id: 3, title: 'Market Info', subtitle: 'Location & Target' },
  { id: 4, title: 'Review', subtitle: 'Summary & Submit' },
]

const DRAFT_KEY = 'startwise_startup_draft'

export default function CreateStartupPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [lastSaved, setLastSaved] = useState<string | null>(null)
  const navigate = useNavigate()
  const createStartupMutation = useCreateStartup()

  // Load initial draft from localStorage if present
  const getSavedDraft = (): Partial<StartupWizardForm> => {
    try {
      const saved = localStorage.getItem(DRAFT_KEY)
      if (saved) return JSON.parse(saved)
    } catch (e) {
      console.error(e)
    }
    return {
      business_name: '',
      business_category: 'Food',
      business_model: 'B2C Retail Outlet',
      description: '',
      investment_amount: 1000000,
      expected_monthly_revenue: 250000,
      expected_expenses: 120000,
      funding_source: 'Self Funded',
      employee_count: 3,
      target_customers: 'Urban professionals & students',
      preferred_location: 'Bengaluru, India',
      competition_level: 'Medium',
      market_demand: 7,
      experience_years: 3,
    }
  }

  const {
    register,
    handleSubmit,
    trigger,
    getValues,
    watch,
    formState: { errors },
  } = useForm<StartupWizardForm>({
    resolver: zodResolver(startupWizardSchema),
    defaultValues: getSavedDraft(),
    mode: 'onTouched',
  })

  const formValues = watch()

  // 30-Second Autosave Draft Logic
  useEffect(() => {
    const timer = setInterval(() => {
      const currentValues = getValues()
      if (currentValues.business_name) {
        localStorage.setItem(DRAFT_KEY, JSON.stringify(currentValues))
        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        setLastSaved(now)
      }
    }, 30000)

    return () => clearInterval(timer)
  }, [getValues])

  const manualSaveDraft = () => {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(getValues()))
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    setLastSaved(now)
    toast.success('Draft saved to local storage!')
  }

  // Validate current step fields before progressing
  const handleNextStep = async () => {
    let fieldsToValidate: (keyof StartupWizardForm)[] = []
    if (currentStep === 1) {
      fieldsToValidate = ['business_name', 'business_category', 'business_model', 'description']
    } else if (currentStep === 2) {
      fieldsToValidate = ['investment_amount', 'expected_monthly_revenue', 'expected_expenses', 'funding_source', 'employee_count']
    } else if (currentStep === 3) {
      fieldsToValidate = ['target_customers', 'preferred_location', 'competition_level', 'market_demand', 'experience_years']
    }

    const isValid = await trigger(fieldsToValidate)
    if (isValid) {
      setCurrentStep((prev) => Math.min(prev + 1, 4))
    } else {
      toast.error('Please fix validation errors before proceeding.')
    }
  }

  const handlePrevStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1))
  }

  const onSubmitForm = (data: StartupWizardForm) => {
    createStartupMutation.mutate(data, {
      onSuccess: (res) => {
        localStorage.removeItem(DRAFT_KEY)
        navigate(`/startup-validation/${res.id}`)
      },
    })
  }

  return (
    <div className="space-y-8 pb-16 max-w-4xl mx-auto">
      <Breadcrumb items={[{ label: 'AI Validation', href: '/startup-validation' }, { label: 'New Startup' }]} />

      {/* Page Title & Draft Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            <BrainCircuit className="h-4 w-4" /> Startup Validation Form Wizard
          </div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white">Create Startup Idea</h1>
        </div>

        <div className="flex items-center gap-3">
          {lastSaved && (
            <Badge variant="glass" className="flex items-center gap-1 text-slate-500">
              <Clock className="h-3 w-3 text-emerald-500" /> Saved {lastSaved}
            </Badge>
          )}
          <Button
            onClick={manualSaveDraft}
            variant="outline"
            size="sm"
            leftIcon={<Save className="h-4 w-4 text-cyan-500" />}
            className="rounded-xl text-xs font-semibold"
          >
            Save Draft
          </Button>
        </div>
      </div>

      {/* Stepper Navigation */}
      <GlassCard className="p-6">
        <Stepper steps={STEPS} currentStep={currentStep} onStepClick={(stepId) => setCurrentStep(stepId)} />
      </GlassCard>

      {/* Multi-Step Form */}
      <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-8" noValidate>
        <AnimatePresence mode="wait">
          {/* STEP 1: BUSINESS INFORMATION */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <GlassCard className="p-6 sm:p-8 space-y-6">
                <div className="border-b border-slate-200/80 dark:border-zinc-800 pb-4">
                  <h3 className="text-xl font-extrabold text-slate-900 dark:text-white">Step 1: Business Information</h3>
                  <p className="text-xs text-slate-500">Enter basic startup identity and category parameters.</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <Input
                    label="Business Name"
                    placeholder="e.g. GreenTech Hydroponics"
                    leftIcon={<Building2 className="h-4 w-4 text-slate-400" />}
                    error={errors.business_name?.message}
                    required
                    {...register('business_name')}
                  />

                  <Select
                    label="Business Category"
                    options={[
                      { label: 'Food & Beverage', value: 'Food' },
                      { label: 'Retail & Consumer Goods', value: 'Retail' },
                      { label: 'Technology & SaaS', value: 'Technology' },
                      { label: 'Healthcare & Wellness', value: 'Healthcare' },
                      { label: 'Education & EdTech', value: 'Education' },
                      { label: 'Agriculture & AgriTech', value: 'Agriculture' },
                      { label: 'Services & Salon', value: 'Services' },
                    ]}
                    error={errors.business_category?.message}
                    {...register('business_category')}
                  />
                </div>

                <Input
                  label="Business Operating Model"
                  placeholder="e.g. B2B Subscription, FOFO Franchise, Direct-to-Consumer"
                  leftIcon={<Briefcase className="h-4 w-4 text-slate-400" />}
                  error={errors.business_model?.message}
                  required
                  {...register('business_model')}
                />

                <Textarea
                  label="Business Description & Unique Selling Proposition (USP)"
                  placeholder="Explain your product/service features, competitive edge, and core mission (min 10 characters)..."
                  rows={4}
                  error={errors.description?.message}
                  {...register('description')}
                />
              </GlassCard>
            </motion.div>
          )}

          {/* STEP 2: FINANCIAL INFORMATION */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <GlassCard className="p-6 sm:p-8 space-y-6">
                <div className="border-b border-slate-200/80 dark:border-zinc-800 pb-4">
                  <h3 className="text-xl font-extrabold text-slate-900 dark:text-white">Step 2: Financial Information</h3>
                  <p className="text-xs text-slate-500">Provide initial capital budget and projected monthly financial figures.</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <Input
                    label="Capital Investment Amount (₹ INR)"
                    type="number"
                    placeholder="1000000"
                    leftIcon={<DollarSign className="h-4 w-4 text-slate-400" />}
                    error={errors.investment_amount?.message}
                    required
                    {...register('investment_amount')}
                  />

                  <Select
                    label="Primary Funding Source"
                    options={[
                      { label: 'Self Funded / Bootstrapped', value: 'Self Funded' },
                      { label: 'Bank Business Loan', value: 'Bank Loan' },
                      { label: 'Angel Investors / VC', value: 'Angel Investor' },
                      { label: 'Friends & Family', value: 'Friends & Family' },
                    ]}
                    error={errors.funding_source?.message}
                    {...register('funding_source')}
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <Input
                    label="Expected Monthly Revenue (₹ INR)"
                    type="number"
                    placeholder="250000"
                    leftIcon={<TrendingUp className="h-4 w-4 text-slate-400" />}
                    error={errors.expected_monthly_revenue?.message}
                    required
                    {...register('expected_monthly_revenue')}
                  />

                  <Input
                    label="Expected Monthly Operating Expenses (₹ INR)"
                    type="number"
                    placeholder="120000"
                    leftIcon={<DollarSign className="h-4 w-4 text-slate-400" />}
                    error={errors.expected_expenses?.message}
                    required
                    {...register('expected_expenses')}
                  />
                </div>

                <Input
                  label="Initial Employee Team Count"
                  type="number"
                  placeholder="3"
                  leftIcon={<Users className="h-4 w-4 text-slate-400" />}
                  error={errors.employee_count?.message}
                  {...register('employee_count')}
                />
              </GlassCard>
            </motion.div>
          )}

          {/* STEP 3: MARKET INFORMATION */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <GlassCard className="p-6 sm:p-8 space-y-6">
                <div className="border-b border-slate-200/80 dark:border-zinc-800 pb-4">
                  <h3 className="text-xl font-extrabold text-slate-900 dark:text-white">Step 3: Market Information</h3>
                  <p className="text-xs text-slate-500">Demographic targets, location preferences, and team background.</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <Input
                    label="Target Customer Segment"
                    placeholder="e.g. Urban Tech Workers (22-45 yrs)"
                    leftIcon={<Users className="h-4 w-4 text-slate-400" />}
                    error={errors.target_customers?.message}
                    required
                    {...register('target_customers')}
                  />

                  <Input
                    label="Preferred Location / City"
                    placeholder="e.g. Indiranagar, Bengaluru"
                    leftIcon={<MapPin className="h-4 w-4 text-slate-400" />}
                    error={errors.preferred_location?.message}
                    required
                    {...register('preferred_location')}
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <Select
                    label="Market Competition Level"
                    options={[
                      { label: 'Low Competition (Niche Market)', value: 'Low' },
                      { label: 'Medium Competition (Moderate Competitors)', value: 'Medium' },
                      { label: 'High Competition (Saturated Market)', value: 'High' },
                    ]}
                    error={errors.competition_level?.message}
                    {...register('competition_level')}
                  />

                  <Input
                    label="Founder Experience (Years in Sector)"
                    type="number"
                    placeholder="3"
                    leftIcon={<Award className="h-4 w-4 text-slate-400" />}
                    error={errors.experience_years?.message}
                    {...register('experience_years')}
                  />
                </div>
              </GlassCard>
            </motion.div>
          )}

          {/* STEP 4: REVIEW & SUBMIT */}
          {currentStep === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <GlassCard className="p-6 sm:p-8 space-y-6">
                <div className="border-b border-slate-200/80 dark:border-zinc-800 pb-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-extrabold text-slate-900 dark:text-white">Step 4: Review Startup Summary</h3>
                    <p className="text-xs text-slate-500">Verify your startup parameters before running AI validation.</p>
                  </div>
                  <Badge variant="success" className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Ready For Submission
                  </Badge>
                </div>

                <div className="space-y-6 text-xs sm:text-sm">
                  {/* Business Summary */}
                  <div className="p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 space-y-2 border border-slate-200/60">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-slate-900 dark:text-white uppercase text-[10px] tracking-wider text-cyan-600">
                        1. Business Identity
                      </span>
                      <button type="button" onClick={() => setCurrentStep(1)} className="text-[10px] font-bold text-cyan-600 hover:underline">
                        Edit Step 1
                      </button>
                    </div>
                    <p><span className="text-slate-400">Name:</span> <strong>{formValues.business_name}</strong></p>
                    <p><span className="text-slate-400">Category:</span> {formValues.business_category} ({formValues.business_model})</p>
                    <p><span className="text-slate-400">Description:</span> {formValues.description}</p>
                  </div>

                  {/* Financial Summary */}
                  <div className="p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 space-y-2 border border-slate-200/60">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-slate-900 dark:text-white uppercase text-[10px] tracking-wider text-cyan-600">
                        2. Financial Structure
                      </span>
                      <button type="button" onClick={() => setCurrentStep(2)} className="text-[10px] font-bold text-cyan-600 hover:underline">
                        Edit Step 2
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <p><span className="text-slate-400">Investment:</span> <strong>₹{formValues.investment_amount?.toLocaleString()}</strong></p>
                      <p><span className="text-slate-400">Funding:</span> {formValues.funding_source}</p>
                      <p><span className="text-slate-400">Est. Revenue:</span> ₹{formValues.expected_monthly_revenue?.toLocaleString()}/mo</p>
                      <p><span className="text-slate-400">Est. Expenses:</span> ₹{formValues.expected_expenses?.toLocaleString()}/mo</p>
                    </div>
                  </div>

                  {/* Market Summary */}
                  <div className="p-4 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 space-y-2 border border-slate-200/60">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-slate-900 dark:text-white uppercase text-[10px] tracking-wider text-cyan-600">
                        3. Market & Location
                      </span>
                      <button type="button" onClick={() => setCurrentStep(3)} className="text-[10px] font-bold text-cyan-600 hover:underline">
                        Edit Step 3
                      </button>
                    </div>
                    <p><span className="text-slate-400">Location:</span> <strong>{formValues.preferred_location}</strong></p>
                    <p><span className="text-slate-400">Target Segment:</span> {formValues.target_customers}</p>
                    <p><span className="text-slate-400">Competition:</span> {formValues.competition_level} Risk</p>
                  </div>
                </div>

                <Button
                  type="submit"
                  size="lg"
                  isLoading={createStartupMutation.isPending}
                  rightIcon={<Sparkles className="h-5 w-5" />}
                  className="w-full bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-2xl py-4 shadow-xl shadow-cyan-500/25"
                >
                  Save & Validate Startup Idea
                </Button>
              </GlassCard>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Wizard Footer Controls */}
        <div className="flex items-center justify-between pt-2">
          {currentStep > 1 ? (
            <Button
              type="button"
              onClick={handlePrevStep}
              variant="outline"
              leftIcon={<ArrowLeft className="h-4 w-4" />}
              className="rounded-xl text-xs font-semibold"
            >
              Previous Step
            </Button>
          ) : <div />}

          {currentStep < 4 && (
            <Button
              type="button"
              onClick={handleNextStep}
              rightIcon={<ArrowRight className="h-4 w-4" />}
              className="bg-cyan-500 hover:bg-cyan-600 text-white font-semibold rounded-xl text-xs shadow-md"
            >
              Next Step
            </Button>
          )}
        </div>
      </form>
    </div>
  )
}
