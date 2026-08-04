/**
 * STARTWISE AI — Franchise Discovery Page Component
 * Franchise search, budget slider, industry pills, and match cards.
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Store, Search, ShieldCheck, MapPin, ExternalLink, ArrowRight } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { GlassCard } from '@/components/ui/Card'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'

const CATEGORIES = ['All', 'Food', 'Retail', 'Healthcare', 'Services']

const MOCK_FRANCHISES = [
  {
    id: '1',
    name: 'Tea Time',
    category: 'Food',
    minInvestment: '₹4 Lakhs',
    maxInvestment: '₹6 Lakhs',
    roi: '45.0%',
    risk: 'Low',
    location: 'Hyderabad, TS',
    website: 'https://teatime.in',
    logo: '☕',
    description: "India's largest tea chain with over 3,000+ outlets serving tea, coffee, and snacks.",
    advantages: ['Low capital required', 'Quick payback within 6-9 months', 'Turnkey setup & training'],
  },
  {
    id: '2',
    name: 'DTDC Express',
    category: 'Retail',
    minInvestment: '₹1.5 Lakhs',
    maxInvestment: '₹3 Lakhs',
    roi: '35.0%',
    risk: 'Low',
    location: 'Bengaluru, KA',
    website: 'https://dtdc.in',
    logo: '📦',
    description: 'Leading courier, parcel, and express delivery logistics provider serving 12,000+ pin codes.',
    advantages: ['Established brand trust', 'Minimal infrastructure risk', 'Steady B2B order flow'],
  },
  {
    id: '3',
    name: 'Lenskart',
    category: 'Healthcare',
    minInvestment: '₹30 Lakhs',
    maxInvestment: '₹45 Lakhs',
    roi: '32.0%',
    risk: 'Medium',
    location: 'Gurugram, HR',
    website: 'https://lenskart.com',
    logo: '👓',
    description: 'Premier tech-enabled eyewear retailer providing prescription glasses and sunglasses.',
    advantages: ['Zero inventory risk FOFO model', 'Automated optical testing machines supplied'],
  },
  {
    id: '4',
    name: 'Amul Scoop Parlour',
    category: 'Food',
    minInvestment: '₹2 Lakhs',
    maxInvestment: '₹5 Lakhs',
    roi: '40.0%',
    risk: 'Low',
    location: 'Anand, GJ',
    website: 'https://amul.com',
    logo: '🍦',
    description: 'Exclusive Amul ice cream & dairy scoop parlours with zero royalty fees.',
    advantages: ['No royalty or profit sharing', 'Massive brand pull across India'],
  },
]

export default function FranchisePage() {
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFranchise, setSelectedFranchise] = useState<any | null>(null)

  const filtered = MOCK_FRANCHISES.filter((f) => {
    const categoryMatch = selectedCategory === 'All' || f.category === selectedCategory
    const searchMatch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) || f.description.toLowerCase().includes(searchQuery.toLowerCase())
    return categoryMatch && searchMatch
  })

  return (
    <div className="space-y-8 pb-12">
      <Breadcrumb items={[{ label: 'Franchise Discovery Hub' }]} />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            <Store className="h-4 w-4" /> Verified Franchise Database
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
            Match Profitable Franchises
          </h1>
          <p className="text-sm text-slate-500 dark:text-zinc-400">
            Discover top-rated franchise opportunities aligned with your budget and city preference.
          </p>
        </div>
      </div>

      {/* Search & Category Filter Bar */}
      <GlassCard className="p-4 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <div className="flex-1 w-full">
            <Input
              type="text"
              placeholder="Search by franchise brand or keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-slate-400" />}
              id="franchise-search"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                  selectedCategory === cat
                    ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md'
                    : 'bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </GlassCard>

      {/* Franchise Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {filtered.map((item) => (
          <motion.div key={item.id} whileHover={{ y: -4 }}>
            <GlassCard className="p-6 space-y-5 h-full flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 text-2xl flex items-center justify-center shadow-sm">
                      {item.logo}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-900 dark:text-white">{item.name}</h3>
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <MapPin className="h-3.5 w-3.5 text-cyan-500" /> {item.location}
                      </div>
                    </div>
                  </div>

                  <Badge variant={item.risk === 'Low' ? 'success' : 'warning'}>
                    {item.risk} Risk
                  </Badge>
                </div>

                <p className="text-xs sm:text-sm text-slate-600 dark:text-zinc-300 leading-relaxed">
                  {item.description}
                </p>

                <div className="grid grid-cols-2 gap-3 p-3 rounded-2xl bg-slate-50 dark:bg-zinc-800/60 text-xs">
                  <div>
                    <span className="text-slate-400 font-medium">Investment Range</span>
                    <p className="font-bold text-slate-900 dark:text-white mt-0.5">{item.minInvestment} - {item.maxInvestment}</p>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">Expected Annual ROI</span>
                    <p className="font-bold text-cyan-600 dark:text-cyan-400 mt-0.5">{item.roi}</p>
                  </div>
                </div>

                <div className="space-y-1.5 text-xs">
                  <p className="font-bold text-slate-700 dark:text-zinc-300">Key Advantages:</p>
                  {item.advantages.map((adv, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-slate-600 dark:text-zinc-400">
                      <ShieldCheck className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                      <span>{adv}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 flex items-center justify-between border-t border-slate-100 dark:border-zinc-800">
                <a
                  href={item.website}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline"
                >
                  Official Site <ExternalLink className="h-3 w-3" />
                </a>

                <Button
                  onClick={() => setSelectedFranchise(item)}
                  size="sm"
                  rightIcon={<ArrowRight className="h-4 w-4" />}
                  className="bg-cyan-500 hover:bg-cyan-600 text-white font-semibold rounded-xl text-xs"
                >
                  Request Info
                </Button>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Info Request Modal */}
      <Modal
        isOpen={!!selectedFranchise}
        onClose={() => setSelectedFranchise(null)}
        title={`Request Info: ${selectedFranchise?.name}`}
        description="Our team will connect you directly with the official brand onboarding manager."
      >
        <div className="space-y-4 pt-2">
          <Input label="Your Contact Name" defaultValue="Vikram Sharma" />
          <Input label="Phone Number" defaultValue="+91 98765 43210" />
          <Input label="Preferred Territory City" defaultValue={selectedFranchise?.location || 'Hyderabad'} />
          <Button
            onClick={() => {
              setSelectedFranchise(null)
            }}
            fullWidth
            className="bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold rounded-xl py-3 mt-2"
          >
            Submit Interest Inquiry
          </Button>
        </div>
      </Modal>
    </div>
  )
}
