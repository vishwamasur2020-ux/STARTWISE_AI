/**
 * STARTWISE AI — Edit Startup Idea Page Component
 * Form view prefilled with existing startup parameters.
 */

import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Building2, MapPin, DollarSign, Users, Award, Save, ArrowLeft } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { GlassCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Skeleton } from '@/components/ui/Skeleton'
import { useStartupDetails, useUpdateStartup } from '@/hooks/useStartups'

const editSchema = z.object({
  business_name: z.string().min(2, 'Business name required'),
  business_category: z.string().min(1, 'Category required'),
  business_model: z.string().min(2, 'Business model required'),
  investment_amount: z.coerce.number().gt(0, 'Investment must be greater than 0'),
  preferred_location: z.string().min(2, 'Location required'),
  target_customers: z.string().min(2, 'Target customers required'),
  experience_years: z.coerce.number().min(0, 'Experience years cannot be negative'),
  expected_monthly_revenue: z.coerce.number().min(0, 'Expected revenue required'),
  description: z.string().optional(),
})

type EditForm = z.infer<typeof editSchema>

export default function EditStartupPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: startup, isLoading } = useStartupDetails(id || '')
  const updateMutation = useUpdateStartup()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EditForm>({
    resolver: zodResolver(editSchema),
  })

  useEffect(() => {
    if (startup) {
      reset({
        business_name: startup.business_name,
        business_category: startup.business_category,
        business_model: startup.business_model,
        investment_amount: startup.investment_amount,
        preferred_location: startup.preferred_location,
        target_customers: startup.target_customers,
        experience_years: startup.experience_years,
        expected_monthly_revenue: startup.expected_monthly_revenue,
        description: startup.description || '',
      })
    }
  }, [startup, reset])

  const onSubmit = (data: EditForm) => {
    if (!id) return
    updateMutation.mutate(
      { id, data },
      {
        onSuccess: () => navigate(`/startup-validation/${id}`),
      }
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-3xl mx-auto py-8">
        <Skeleton className="h-8 w-64 rounded-xl" />
        <Skeleton className="h-96 w-full rounded-3xl" />
      </div>
    )
  }

  return (
    <div className="space-y-8 pb-16 max-w-3xl mx-auto">
      <Breadcrumb
        items={[
          { label: 'AI Validation', href: '/startup-validation' },
          { label: 'My Startups', href: '/startup-validation/history' },
          { label: 'Edit Idea' },
        ]}
      />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white">Edit Startup Idea</h1>
          <p className="text-xs text-slate-500">Update parameters for {startup?.business_name}</p>
        </div>
        <Button
          onClick={() => navigate(-1)}
          variant="outline"
          size="sm"
          leftIcon={<ArrowLeft className="h-4 w-4" />}
          className="rounded-xl text-xs"
        >
          Cancel
        </Button>
      </div>

      <GlassCard className="p-6 sm:p-8 space-y-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <Input
              label="Business Name"
              leftIcon={<Building2 className="h-4 w-4 text-slate-400" />}
              error={errors.business_name?.message}
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
                { label: 'Services', value: 'Services' },
              ]}
              error={errors.business_category?.message}
              {...register('business_category')}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <Input
              label="Capital Investment Amount (₹ INR)"
              type="number"
              leftIcon={<DollarSign className="h-4 w-4 text-slate-400" />}
              error={errors.investment_amount?.message}
              {...register('investment_amount')}
            />

            <Input
              label="Preferred Location"
              leftIcon={<MapPin className="h-4 w-4 text-slate-400" />}
              error={errors.preferred_location?.message}
              {...register('preferred_location')}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <Input
              label="Target Customer Segment"
              leftIcon={<Users className="h-4 w-4 text-slate-400" />}
              error={errors.target_customers?.message}
              {...register('target_customers')}
            />

            <Input
              label="Founder Experience (Years)"
              type="number"
              leftIcon={<Award className="h-4 w-4 text-slate-400" />}
              error={errors.experience_years?.message}
              {...register('experience_years')}
            />
          </div>

          <Textarea label="Business Description" rows={4} {...register('description')} />

          <Button
            type="submit"
            size="lg"
            isLoading={updateMutation.isPending}
            leftIcon={<Save className="h-5 w-5" />}
            className="w-full bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold rounded-2xl py-4 shadow-xl"
          >
            Save Updated Changes
          </Button>
        </form>
      </GlassCard>
    </div>
  )
}
