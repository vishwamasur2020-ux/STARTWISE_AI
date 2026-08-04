/**
 * STARTWISE AI — Framer Motion Animation Variants
 */

import { Variants } from 'framer-motion'

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
}

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1.0] },
  },
}

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
}

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05,
    },
  },
}

export const floatingAnimation = {
  y: [0, -8, 0],
  transition: {
    duration: 4,
    repeat: Infinity,
    ease: 'easeInOut' as const,
  },
}

export const pulseGlow = {
  boxShadow: [
    '0 0 15px rgba(6, 182, 212, 0.15)',
    '0 0 30px rgba(6, 182, 212, 0.35)',
    '0 0 15px rgba(6, 182, 212, 0.15)',
  ],
  transition: {
    duration: 3,
    repeat: Infinity,
    ease: 'easeInOut' as const,
  },
}
