import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ShieldAlert, AlertCircle, Zap } from 'lucide-react'
import api from '../lib/api'
import RiskPanel from '../components/RiskPanel'
import GlassCard from '../components/bits/GlassCard'

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut'
    }
  }
}

export default function RiskDashboard() {
  const [missions, setMissions] = useState([])
  const [selectedMission, setSelectedMission] = useState(null)
  const [riskData, setRiskData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/missions').then(res => {
      setMissions(res.data)
      if (res.data.length > 0) setSelectedMission(res.data[0].id)
    })
  }, [])

  useEffect(() => {
    if (!selectedMission) return
    setLoading(true)
    api.post('/risk-analysis', { mission_id: selectedMission })
      .then(res => setRiskData(res.data))
      .finally(() => setLoading(false))
  }, [selectedMission])

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-8"
    >
      {/* Premium Page Header */}
      <motion.div variants={itemVariants}>
        <GlassCard className="border-amber-400/20 hover:border-amber-400/30" hover={false}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-12 h-12 bg-gradient-to-br from-amber-400/20 to-orange-400/20 rounded-xl border border-amber-400/30 shadow-lg shadow-amber-500/10">
                <ShieldAlert className="w-6 h-6 text-amber-400" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-amber-400/5 to-transparent pointer-events-none" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-50 tracking-tight mb-1">Risk Assessment Matrix</h2>
                <p className="text-sm text-slate-400">Mission threat analysis & route optimization</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-amber-400/10 border border-amber-400/30 rounded-lg shadow-lg shadow-amber-500/10">
              <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" />
              <span className="text-xs text-amber-400 font-mono font-bold tracking-wider">LIVE MONITORING</span>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Mission Selector */}
      <motion.div variants={itemVariants}>
        <GlassCard className="border-slate-700/50 hover:border-amber-400/20 transition-colors duration-300">
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1">
              <label htmlFor="mission-select" className="block text-xs font-mono text-slate-400 mb-2 uppercase tracking-wider font-semibold">
                Select Mission
              </label>
              <p className="text-xs text-slate-500">Choose a mission to analyze risk factors</p>
            </div>
            <select
              id="mission-select"
              value={selectedMission || ''} 
              onChange={(e) => setSelectedMission(parseInt(e.target.value))} 
              className="bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-3 text-sm text-slate-200 font-medium
                         focus:outline-none focus:border-amber-400/60 focus:ring-2 focus:ring-amber-400/20 focus-visible:ring-2
                         hover:border-amber-400/40 hover:bg-slate-900/80
                         transition-all duration-200 cursor-pointer min-w-[220px] shadow-lg"
            >
              {missions.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
            </select>
          </div>
        </GlassCard>
      </motion.div>

      {/* Content Area */}
      {loading ? (
        <motion.div variants={itemVariants}>
          <GlassCard className="p-16 text-center border-amber-400/20 hover:border-amber-400/30" hover={false}>
            <div className="flex flex-col items-center">
              <div className="relative mb-6">
                <div className="w-20 h-20 rounded-full border-2 border-amber-400/30 border-t-amber-400 animate-spin" />
                <ShieldAlert className="w-9 h-9 text-amber-400 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <h3 className="text-lg font-bold text-slate-100 mb-2">Calculating Risk Profile</h3>
              <p className="text-sm text-slate-400">Analyzing threat vectors and mission parameters...</p>
              <div className="mt-4 flex items-center gap-2 text-xs text-slate-500 font-mono">
                <div className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-pulse" />
                Processing threat intelligence
              </div>
            </div>
          </GlassCard>
        </motion.div>
      ) : !riskData ? (
        <motion.div variants={itemVariants}>
          <GlassCard className="p-16 text-center border-slate-700/30" hover={false}>
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-slate-600" />
            <h3 className="text-lg font-bold text-slate-300 mb-2">No Risk Data Available</h3>
            <p className="text-sm text-slate-500">Select a mission above to view detailed risk analysis</p>
          </GlassCard>
        </motion.div>
      ) : (
        <motion.div variants={itemVariants}>
          <RiskPanel riskData={riskData} />
        </motion.div>
      )}
    </motion.div>
  )
}