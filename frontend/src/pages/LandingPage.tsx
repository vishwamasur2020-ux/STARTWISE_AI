/**
 * STARTWISE AI — Premium Award-Winning Landing Page
 * Full section build: Hero, Trusted Companies, Feature Grid, How-It-Works Timeline,
 * AI Capabilities, Comparison Table, Testimonials, Pricing Tiers, FAQ Accordion, CTA, and Footer.
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  BrainCircuit,
  TrendingUp,
  Store,
  Megaphone,
  FileText,
  CheckCircle2,
  XCircle,
  ChevronDown,
  Zap,
} from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { TRUSTED_COMPANIES, PRICING_TIERS, TESTIMONIALS, FAQS } from '@/constants'
import { slideUp, staggerContainer, floatingAnimation } from '@/animations'

export default function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(0)
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  return (
    <div className="min-h-screen animated-bg text-slate-900 dark:text-white overflow-hidden selection:bg-cyan-500 selection:text-white">
      {/* ── Top Header Navigation ────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 frosted border-b border-slate-200/60 dark:border-white/10 px-6 lg:px-16 h-20 flex items-center justify-between backdrop-blur-xl">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <Sparkles className="h-5 w-5" />
          </div>
          <span className="text-xl font-black tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 dark:from-white dark:to-cyan-200 bg-clip-text text-transparent">
            STARTWISE AI
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-600 dark:text-zinc-300">
          <a href="#features" className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">How It Works</a>
          <a href="#ai-tech" className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">AI Engine</a>
          <a href="#pricing" className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">Pricing</a>
          <a href="#faqs" className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">FAQ</a>
        </nav>

        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm" className="font-semibold text-xs sm:text-sm">
              Sign In
            </Button>
          </Link>
          <Link to="/register">
            <Button
              size="sm"
              className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-semibold rounded-xl text-xs sm:text-sm shadow-md shadow-cyan-500/20"
            >
              Start Free Trial
            </Button>
          </Link>
        </div>
      </header>

      {/* ── HERO SECTION ────────────────────────────────────────────────────── */}
      <section className="relative pt-12 pb-24 px-6 lg:px-16 max-w-7xl mx-auto">
        {/* Subtle background glow Orbs */}
        <div className="absolute top-10 left-1/2 -translate-x-1/2 w-[600px] h-[350px] bg-gradient-to-r from-cyan-500/15 via-blue-500/15 to-indigo-500/15 rounded-full blur-3xl pointer-events-none -z-10" />

        <motion.div
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
          className="text-center max-w-4xl mx-auto space-y-8"
        >
          {/* Badge pill */}
          <motion.div variants={slideUp} className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-card border border-cyan-500/30 bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 text-xs font-bold uppercase tracking-wider shadow-sm">
            <Zap className="h-3.5 w-3.5" /> Next-Gen AI Startup Advisor 2.0
          </motion.div>

          {/* Headline */}
          <motion.h1
            variants={slideUp}
            className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-[1.1]"
          >
            Validate Your Startup.<br />
            <span className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Predict ROI with AI Precision.
            </span>
          </motion.h1>

          <motion.p
            variants={slideUp}
            className="text-base sm:text-xl text-slate-600 dark:text-zinc-300 max-w-2xl mx-auto leading-relaxed font-medium"
          >
            Empowering entrepreneurs and investors with 94.2% accurate ML ROI predictions, smart franchise matching, and executive pitch reports in minutes.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div variants={slideUp} className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link to="/register">
              <Button
                size="lg"
                rightIcon={<ArrowRight className="h-5 w-5" />}
                className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-600 hover:to-indigo-700 text-white font-bold rounded-2xl px-8 py-4 text-base shadow-xl shadow-cyan-500/25"
              >
                Validate Idea Free
              </Button>
            </Link>
            <Link to="/franchise">
              <Button
                variant="outline"
                size="lg"
                leftIcon={<Store className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />}
                className="glass-card border-slate-300 dark:border-white/20 hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-900 dark:text-white font-bold rounded-2xl px-8 py-4 text-base shadow-sm"
              >
                Explore Franchises
              </Button>
            </Link>
          </motion.div>

          {/* Floating Glass Graphic Card */}
          <motion.div
            variants={slideUp}
            animate={floatingAnimation}
            className="mt-14 glass-card p-6 sm:p-10 rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/70 dark:bg-zinc-900/70 backdrop-blur-2xl shadow-2xl relative max-w-4xl mx-auto text-left"
          >
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 border-b border-slate-200/60 dark:border-zinc-800 pb-6 mb-6">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-md">
                  AI
                </div>
                <div>
                  <h3 className="font-extrabold text-lg text-slate-900 dark:text-white">AI Validation Engine</h3>
                  <p className="text-xs text-slate-500 dark:text-zinc-400">Live Model Version 2.4.0 (Trained on 10,000+ Startups)</p>
                </div>
              </div>
              <span className="px-3.5 py-1.5 rounded-full text-xs font-extrabold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300">
                High Confidence Match: 94.2%
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl bg-slate-50/80 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-700/50">
                <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-widest">Success Rate</span>
                <p className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">88.5%</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-50/80 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-700/50">
                <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-widest">Predicted ROI</span>
                <p className="text-2xl font-black text-cyan-600 dark:text-cyan-400 mt-1">42.4% / yr</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-50/80 dark:bg-zinc-800/50 border border-slate-200/60 dark:border-zinc-700/50">
                <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-widest">Market Demand</span>
                <p className="text-2xl font-black text-indigo-600 dark:text-indigo-400 mt-1">9.2 / 10</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* ── TRUSTED COMPANIES LOGO CLOUD ─────────────────────────────────────── */}
      <section className="py-12 border-y border-slate-200/60 dark:border-zinc-800 bg-white/40 dark:bg-zinc-900/40 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-xs font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-widest mb-8">
            Trusted by founders, incubators, and investors worldwide
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8 sm:gap-16 opacity-75">
            {TRUSTED_COMPANIES.map((company, idx) => (
              <span key={idx} className="text-sm sm:text-base font-extrabold tracking-tight text-slate-600 dark:text-zinc-400 hover:opacity-100 transition-opacity cursor-pointer">
                {company.logo}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES SECTION ────────────────────────────────────────────────── */}
      <section id="features" className="py-24 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">
            Complete Feature Suite
          </span>
          <h2 className="text-3xl sm:text-5xl font-black tracking-tight">
            Everything You Need To Build & Scale
          </h2>
          <p className="text-slate-500 dark:text-zinc-400 text-sm sm:text-base">
            From raw concept validation to matching profitable franchise models.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              icon: <BrainCircuit className="h-6 w-6 text-cyan-500" />,
              title: 'AI Startup Validation',
              desc: 'Instant feasibility scoring based on location, budget, market demand, and target customer demographics.',
            },
            {
              icon: <TrendingUp className="h-6 w-6 text-blue-500" />,
              title: 'ML ROI Prediction Engine',
              desc: 'Trained Machine Learning model forecasting annual revenue, ROI payback timeline, and profitability.',
            },
            {
              icon: <ShieldCheck className="h-6 w-6 text-emerald-500" />,
              title: 'Risk Level Analysis',
              desc: 'Comprehensive risk breakdown rating competitor saturation, operational complexity, and market volatility.',
            },
            {
              icon: <Store className="h-6 w-6 text-indigo-500" />,
              title: 'Franchise Finder',
              desc: 'Match with 500+ verified franchise opportunities tailored to your capital budget and preferred city.',
            },
            {
              icon: <Megaphone className="h-6 w-6 text-amber-500" />,
              title: 'AI Marketing Blueprint',
              desc: 'Automated digital & local marketing strategy templates designed for your specific business category.',
            },
            {
              icon: <FileText className="h-6 w-6 text-purple-500" />,
              title: 'Executive PDF Reports',
              desc: 'Generate professional 1-click PDF reports ready to share with bank loan officers and angel investors.',
            },
          ].map((f, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -6 }}
              className="glass-card p-8 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-lg space-y-4"
            >
              <div className="h-12 w-12 rounded-2xl bg-slate-100 dark:bg-zinc-800 flex items-center justify-center shadow-inner">
                {f.icon}
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">{f.title}</h3>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-zinc-400 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS TIMELINE ───────────────────────────────────────────── */}
      <section id="how-it-works" className="py-24 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">
            3-Step Workflow
          </span>
          <h2 className="text-3xl sm:text-5xl font-black tracking-tight">How STARTWISE AI Works</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {[
            { step: '01', title: 'Input Business Parameters', desc: 'Enter your business category, investment capital, target location, and team experience.' },
            { step: '02', title: 'AI Analyzes Data', desc: 'Our ML models cross-reference competitor saturation, regional demand, and financial benchmarks.' },
            { step: '03', title: 'Get Predictions & Report', desc: 'Receive your success probability, ROI prediction, franchise matches, and downloadable PDF report.' },
          ].map((s, idx) => (
            <div key={idx} className="glass-card p-8 rounded-3xl border border-slate-200/60 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-xl space-y-4 relative">
              <span className="text-4xl font-black text-cyan-500/30 dark:text-cyan-400/20">{s.step}</span>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">{s.title}</h3>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-zinc-400 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── WHY CHOOSE STARTWISE AI COMPARISON ───────────────────────────────── */}
      <section className="py-24 px-6 lg:px-16 max-w-5xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-14 space-y-3">
          <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">The Competitive Advantage</span>
          <h2 className="text-3xl sm:text-4xl font-black">Traditional Consultancy vs STARTWISE AI</h2>
        </div>

        <div className="glass-card rounded-3xl border border-slate-200/80 dark:border-white/10 overflow-hidden shadow-2xl">
          <div className="grid grid-cols-3 bg-slate-100/80 dark:bg-zinc-800/80 p-5 font-bold text-xs sm:text-sm border-b border-slate-200/80 dark:border-zinc-700">
            <div>Feature</div>
            <div className="text-center text-slate-500">Traditional Consultancy</div>
            <div className="text-center text-cyan-600 dark:text-cyan-400">STARTWISE AI</div>
          </div>
          {[
            { f: 'Turnaround Time', trad: '3 - 6 Weeks', ai: 'Instant (Under 60 Secs)' },
            { f: 'Cost', trad: '$2,500 - $10,000', ai: 'Free to $29 / mo' },
            { f: 'Accuracy', trad: 'Subjective Opinions', ai: '94.2% Verified ML Precision' },
            { f: 'Franchise Matches', trad: 'Limited Agency Contracts', ai: '500+ Verified Network' },
            { f: 'Report Updates', trad: 'Static Paper Document', ai: 'Live Dynamic Updates' },
          ].map((r, idx) => (
            <div key={idx} className="grid grid-cols-3 p-5 text-xs sm:text-sm border-b border-slate-100 dark:border-zinc-800/60 items-center">
              <div className="font-semibold text-slate-800 dark:text-zinc-200">{r.f}</div>
              <div className="text-center text-slate-500 dark:text-zinc-400 flex items-center justify-center gap-1">
                <XCircle className="h-4 w-4 text-rose-500 hidden sm:inline" /> {r.trad}
              </div>
              <div className="text-center font-bold text-cyan-600 dark:text-cyan-400 flex items-center justify-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 hidden sm:inline" /> {r.ai}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── TESTIMONIALS CAROUSEL ───────────────────────────────────────────── */}
      <section className="py-24 px-6 lg:px-16 max-w-5xl mx-auto text-center">
        <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">Testimonials</span>
        <h2 className="text-3xl sm:text-4xl font-black mb-12">Loved By Founders & Investors</h2>

        <div className="glass-card p-8 sm:p-12 rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl shadow-2xl relative">
          <div className="flex justify-center text-amber-400 mb-4 text-sm">
            {'⭐'.repeat(TESTIMONIALS[currentTestimonial].rating)}
          </div>
          <p className="text-base sm:text-xl font-medium text-slate-800 dark:text-zinc-200 leading-relaxed italic mb-8 max-w-3xl mx-auto">
            "{TESTIMONIALS[currentTestimonial].quote}"
          </p>
          <div className="flex items-center justify-center gap-4">
            <img src={TESTIMONIALS[currentTestimonial].avatar} alt="" className="h-12 w-12 rounded-full object-cover ring-2 ring-cyan-500/30" />
            <div className="text-left">
              <p className="font-bold text-sm text-slate-900 dark:text-white">{TESTIMONIALS[currentTestimonial].author}</p>
              <p className="text-xs text-slate-500 dark:text-zinc-400">{TESTIMONIALS[currentTestimonial].role}</p>
            </div>
          </div>

          <div className="flex justify-center gap-2 mt-8">
            {TESTIMONIALS.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentTestimonial(i)}
                className={`h-2.5 rounded-full transition-all ${i === currentTestimonial ? 'w-8 bg-cyan-500' : 'w-2.5 bg-slate-300 dark:bg-zinc-700'}`}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ── PRICING SECTION ─────────────────────────────────────────────────── */}
      <section id="pricing" className="py-24 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">Transparent Pricing</span>
          <h2 className="text-3xl sm:text-5xl font-black">Choose The Right Plan</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {PRICING_TIERS.map((tier) => (
            <div
              key={tier.id}
              className={`glass-card p-8 rounded-3xl border ${tier.isPopular ? 'border-cyan-500 shadow-2xl shadow-cyan-500/15 ring-2 ring-cyan-500/20' : 'border-slate-200/80 dark:border-white/10'} bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl flex flex-col justify-between space-y-6 relative`}
            >
              {tier.isPopular && (
                <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-widest bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md">
                  Most Popular
                </span>
              )}

              <div className="space-y-4">
                <h3 className="text-2xl font-black text-slate-900 dark:text-white">{tier.name}</h3>
                <p className="text-xs text-slate-500 dark:text-zinc-400">{tier.description}</p>
                <div className="flex items-baseline gap-1 pt-2">
                  <span className="text-4xl font-black text-slate-900 dark:text-white">{tier.price}</span>
                  <span className="text-xs text-slate-400 font-medium">/{tier.period}</span>
                </div>

                <ul className="space-y-3 pt-4 border-t border-slate-100 dark:border-zinc-800 text-xs">
                  {tier.features.map((feat, i) => (
                    <li key={i} className="flex items-center gap-2.5 text-slate-700 dark:text-zinc-300 font-medium">
                      <CheckCircle2 className="h-4 w-4 text-cyan-500 flex-shrink-0" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <Link to="/register">
                <Button
                  fullWidth
                  className={tier.isPopular ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold rounded-xl py-3 shadow-md' : 'bg-slate-100 dark:bg-zinc-800 text-slate-900 dark:text-white font-bold rounded-xl py-3 hover:bg-slate-200'}
                >
                  {tier.cta}
                </Button>
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* ── FAQ ACCORDION SECTION ────────────────────────────────────────────── */}
      <section id="faqs" className="py-24 px-6 lg:px-16 max-w-4xl mx-auto">
        <div className="text-center mb-14 space-y-3">
          <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest">Got Questions?</span>
          <h2 className="text-3xl sm:text-4xl font-black">Frequently Asked Questions</h2>
        </div>

        <div className="space-y-4">
          {FAQS.map((faq, idx) => (
            <div key={idx} className="glass-card rounded-2xl border border-slate-200/80 dark:border-white/10 overflow-hidden shadow-sm">
              <button
                onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                className="w-full text-left p-6 font-bold text-sm sm:text-base flex items-center justify-between gap-4 text-slate-900 dark:text-white"
              >
                <span>{faq.question}</span>
                <ChevronDown className={`h-5 w-5 text-cyan-500 transition-transform ${openFaq === idx ? 'rotate-180' : ''}`} />
              </button>

              <AnimatePresence>
                {openFaq === idx && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="px-6 pb-6 text-xs sm:text-sm text-slate-600 dark:text-zinc-400 leading-relaxed border-t border-slate-100 dark:border-zinc-800/60 pt-4"
                  >
                    {faq.answer}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </section>

      {/* ── CALL TO ACTION ──────────────────────────────────────────────────── */}
      <section className="py-20 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="glass-card p-10 sm:p-16 rounded-3xl border border-cyan-500/30 bg-gradient-to-r from-cyan-600 via-blue-700 to-indigo-800 text-white text-center shadow-2xl relative overflow-hidden">
          <div className="max-w-3xl mx-auto space-y-6 relative z-10">
            <h2 className="text-3xl sm:text-5xl font-black tracking-tight">Ready To Validate Your Startup Idea?</h2>
            <p className="text-cyan-100 text-sm sm:text-base">Join over 10,000+ founders making data-driven decisions today.</p>
            <Link to="/register">
              <Button size="lg" className="bg-white text-slate-900 hover:bg-cyan-50 font-bold rounded-2xl px-8 py-4 text-base shadow-xl">
                Get Started Free →
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ── FOOTER ──────────────────────────────────────────────────────────── */}
      <footer className="border-t border-slate-200/80 dark:border-zinc-800 py-12 px-6 lg:px-16 text-xs text-slate-500 dark:text-zinc-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-cyan-500" />
            <span className="font-bold text-slate-900 dark:text-white">STARTWISE AI © 2026</span>
          </div>
          <div className="flex gap-6">
            <a href="#features" className="hover:underline">Privacy Policy</a>
            <a href="#features" className="hover:underline">Terms of Service</a>
            <a href="#features" className="hover:underline">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
