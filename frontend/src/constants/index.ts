/**
 * STARTWISE AI — Design System Constants & Mock Data
 */

export const BRAND_NAME = 'STARTWISE AI'

export const TRUSTED_COMPANIES = [
  { name: 'Y Combinator', logo: '🚀 YC Backed' },
  { name: 'Techstars', logo: '⚡ Techstars' },
  { name: 'Sequoia', logo: '🌲 Sequoia' },
  { name: 'Accel', logo: '💎 Accel' },
  { name: 'SoftBank', logo: '🌐 SoftBank' },
  { name: 'NASSCOM', logo: '🇮🇳 NASSCOM' },
]

export const PRICING_TIERS = [
  {
    id: 'free',
    name: 'Starter',
    price: '$0',
    period: 'forever free',
    description: 'Perfect for aspiring founders exploring initial startup concepts.',
    features: [
      '1 Startup Idea Validation per month',
      'Basic ROI & Risk calculation',
      'Top 3 Franchise Recommendations',
      'Community Support Access',
    ],
    cta: 'Get Started Free',
    isPopular: false,
  },
  {
    id: 'pro',
    name: 'Pro Entrepreneur',
    price: '$29',
    period: 'per month',
    description: 'Everything you need to rigorously validate and scale your business.',
    features: [
      'Unlimited AI Startup Validations',
      '94.2% Accurate ML ROI Predictions',
      'Full Franchise Database Access (500+)',
      'AI Marketing Strategy Generator',
      'Downloadable Executive PDF Reports',
      'Priority Support 24/7',
    ],
    cta: 'Start 14-Day Free Trial',
    isPopular: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise & Investor',
    price: '$99',
    period: 'per month',
    description: 'Tailored for incubators, investors, and multi-unit franchise buyers.',
    features: [
      'Everything in Pro Plan',
      'Custom ML Model Fine-tuning',
      'Multi-user Team Workspace (5 Seats)',
      'API Access for Automated Pitch Decks',
      'Dedicated Investment Advisor',
      'Custom SLA & Onboarding',
    ],
    cta: 'Contact Sales',
    isPopular: false,
  },
]

export const TESTIMONIALS = [
  {
    quote: 'STARTWISE AI saved me from investing ₹25L in a saturated market. The ML competition score was spot-on!',
    author: 'Vikram Sharma',
    role: 'Founder, RetailTech Solutions',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
    rating: 5,
  },
  {
    quote: 'The franchise recommendation engine matched me with a high-ROI tea parlour chain in under 3 minutes.',
    author: 'Priya Patel',
    role: 'Multi-Unit Franchise Owner',
    avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80',
    rating: 5,
  },
  {
    quote: 'Generating executive PDF reports for my investors used to take days. Now it happens with one click.',
    author: 'Rajesh Nair',
    role: 'Angel Investor & Advisor',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80',
    rating: 5,
  },
]

export const FAQS = [
  {
    question: 'How does STARTWISE AI predict startup success probability?',
    answer: 'Our proprietary ML model analyzes historical market data, customer acquisition costs, investment ratios, and local competitor density to produce a 94.2% accurate success probability score.',
  },
  {
    question: 'Can I export reports for pitch decks and bank loan applications?',
    answer: 'Yes! Pro and Enterprise users can instantly download comprehensive, beautifully formatted PDF executive reports with full financial breakdowns.',
  },
  {
    question: 'How are franchise recommendations matched to my profile?',
    answer: 'Our matching algorithm checks your available capital budget, target city, risk tolerance, and expected ROI percentage against our database of 500+ verified franchises.',
  },
  {
    question: 'Is my startup idea kept confidential?',
    answer: 'Absolutely. We enforce bank-grade AES-256 encryption. Your startup inputs are never shared with third parties or trained on public models.',
  },
]
