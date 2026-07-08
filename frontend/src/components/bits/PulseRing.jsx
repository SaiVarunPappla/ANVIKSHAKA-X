import React from 'react'
import { motion } from 'framer-motion'

export default function PulseRing({ size = 40, color = '#38bdf8' }) {
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {[0, 1, 2].map(i => (
        <motion.div
          key={i}
          className="absolute rounded-full border"
          style={{ borderColor: color }}
          initial={{ scale: 1, opacity: 0.8 }}
          animate={{ scale: 2.5, opacity: 0 }}
          transition={{ duration: 2, repeat: Infinity, delay: i * 0.6, ease: 'easeOut' }}
        />
      ))}
      <div className="w-2 h-2 rounded-full" style={{ background: color }} />
    </div>
  )
}
