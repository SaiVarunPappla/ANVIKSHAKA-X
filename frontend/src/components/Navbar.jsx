import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const pageTitles = {
  '/': 'Command Dashboard',
  '/mission-planner': 'Mission Planning Console',
  '/risk': 'Risk Assessment Matrix',
  '/maintenance': 'Predictive Maintenance Centre',
  '/analytics': 'Fleet Analytics & Intelligence',
  '/chat': 'ANVIKSHA AI Assistant'
}

export default function Navbar() {
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'ANVIKSHAKA-X'
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header className="h-16 bg-slate-800/50 backdrop-blur-xl border-b border-slate-700/60 flex items-center justify-between px-6 sticky top-0 z-40 shadow-[0_4px_16px_rgba(0,0,0,0.3)]">
      {/* Title with page transition */}
      <AnimatePresence mode="wait">
        <motion.h2 
          key={location.pathname}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
          className="text-lg font-bold text-slate-50 tracking-tight"
        >
          {title}
        </motion.h2>
      </AnimatePresence>
      
      {/* Clock */}
      <div className="text-right">
        <motion.p 
          key={time.toLocaleTimeString('en-GB')}
          initial={{ opacity: 0.8 }}
          animate={{ opacity: 1 }}
          className="text-sm font-mono font-bold text-sky-400 tabular-nums"
        >
          {time.toLocaleTimeString('en-GB')}
        </motion.p>
        <p className="text-[10px] font-mono text-slate-500 tracking-wider">UTC</p>
      </div>
    </header>
  )
}