import { motion } from 'framer-motion'
import { MapPin, Route, TrendingUp, AlertTriangle } from 'lucide-react'
import GlassCard from './bits/GlassCard'

const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: 'easeOut'
    }
  }
}

const zoneVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: (i) => ({
    opacity: 1,
    x: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.3,
      ease: 'easeOut'
    }
  })
}

export default function RiskPanel({ riskData }) {
  if (!riskData) return null

  const riskScore = riskData.risk_score?.toFixed(0) || 'N/A'
  const successProb = riskData.success_probability?.toFixed(1) || 'N/A'
  const hasZones = riskData.high_risk_zones && riskData.high_risk_zones.length > 0

  // Determine risk level color
  const riskLevel = riskScore >= 70 ? 'high' : riskScore >= 40 ? 'medium' : 'low'
  const riskColors = {
    high: 'text-red-400 border-red-400/40 bg-red-400/10',
    medium: 'text-amber-400 border-amber-400/40 bg-amber-400/10',
    low: 'text-green-400 border-green-400/40 bg-green-400/10'
  }
  
  const riskGlow = {
    high: 'shadow-[0_0_30px_rgba(248,113,113,0.2)]',
    medium: 'shadow-[0_0_30px_rgba(251,191,36,0.2)]',
    low: 'shadow-[0_0_30px_rgba(34,197,94,0.2)]'
  }

  return (
    <div className="space-y-6">
      {/* Risk Score & Success Probability */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Score Card */}
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
        >
          <GlassCard className={`border-2 ${riskColors[riskLevel]} ${riskGlow[riskLevel]} hover:scale-[1.02] transition-all duration-300`} hover={false}>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-6">
                <AlertTriangle className={`w-5 h-5 ${riskLevel === 'high' ? 'text-red-400' : riskLevel === 'medium' ? 'text-amber-400' : 'text-green-400'}`} />
                <h3 className="text-sm font-mono text-slate-300 uppercase tracking-widest font-bold">Risk Score</h3>
              </div>
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.5, ease: 'easeOut' }}
                className={`text-7xl font-black font-mono mb-3 tracking-tight ${riskLevel === 'high' ? 'text-red-400' : riskLevel === 'medium' ? 'text-amber-400' : 'text-green-400'}`}
              >
                {riskScore}
              </motion.div>
              <div className="text-xs font-mono text-slate-500 tracking-wider mb-6">
                / 100 THREAT INDEX
              </div>
              <div className="pt-5 border-t border-slate-700/50">
                <span className={`inline-flex items-center px-4 py-2 rounded-full text-xs font-black uppercase tracking-wider border-2 ${riskColors[riskLevel]} transition-all duration-300 hover:scale-105`}>
                  <span className={`w-2 h-2 rounded-full mr-2 ${riskLevel === 'high' ? 'bg-red-400' : riskLevel === 'medium' ? 'bg-amber-400' : 'bg-green-400'} animate-pulse`} />
                  {riskLevel} RISK
                </span>
              </div>
            </div>
          </GlassCard>
        </motion.div>

        {/* Success Probability Card */}
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.1 }}
        >
          <GlassCard className="border-2 border-green-400/40 bg-green-400/10 shadow-[0_0_30px_rgba(34,197,94,0.2)] hover:scale-[1.02] transition-all duration-300" hover={false}>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-6">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <h3 className="text-sm font-mono text-slate-300 uppercase tracking-widest font-bold">Success Rate</h3>
              </div>
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.5, ease: 'easeOut' }}
                className="text-7xl font-black text-green-400 font-mono mb-3 tracking-tight"
              >
                {successProb}
                <span className="text-4xl">%</span>
              </motion.div>
              <div className="text-xs font-mono text-slate-500 tracking-wider mb-6">
                MISSION COMPLETION PROBABILITY
              </div>
              <div className="pt-5 border-t border-slate-700/50">
                <div className="w-full bg-slate-900/80 rounded-full h-3 overflow-hidden border border-slate-700/50">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${successProb}%` }}
                    transition={{ delay: 0.5, duration: 1, ease: 'easeOut' }}
                    className="h-full bg-gradient-to-r from-green-500 via-green-400 to-emerald-400 rounded-full relative overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                  </motion.div>
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>

      {/* High-Risk Zones */}
      {hasZones && (
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.2 }}
        >
          <GlassCard className="border-red-400/30 hover:border-red-400/40 transition-colors duration-300">
            <div className="flex items-center gap-3 mb-5 pb-4 border-b border-slate-700/50">
              <div className="flex items-center justify-center w-10 h-10 bg-red-400/10 rounded-xl border border-red-400/30 shadow-lg shadow-red-500/10">
                <MapPin className="w-5 h-5 text-red-400" />
              </div>
              <div className="flex-1">
                <h4 className="text-base font-bold text-slate-100">High-Risk Zones</h4>
                <p className="text-xs text-slate-500 font-mono mt-0.5">Areas requiring elevated caution</p>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-red-400/10 border border-red-400/30 rounded-lg">
                <span className="text-xs font-bold text-red-400 font-mono">{riskData.high_risk_zones.length} ZONES</span>
              </div>
            </div>
            <div className="space-y-3">
              {riskData.high_risk_zones.map((zone, i) => (
                <motion.div
                  key={i}
                  custom={i}
                  variants={zoneVariants}
                  initial="hidden"
                  animate="visible"
                  className="group flex items-start gap-3 p-4 bg-red-400/5 border border-red-400/30 rounded-xl hover:bg-red-400/10 hover:border-red-400/50 hover:shadow-lg hover:shadow-red-500/10 transition-all duration-300 cursor-pointer"
                >
                  <div className="flex-shrink-0 w-7 h-7 flex items-center justify-center bg-red-400/20 rounded-lg border border-red-400/40 mt-0.5 group-hover:scale-110 transition-transform duration-200">
                    <span className="text-sm font-black text-red-400">{i + 1}</span>
                  </div>
                  <p className="text-sm text-slate-200 flex-1 leading-relaxed font-medium">{zone}</p>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Route Suggestion */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.3 }}
      >
        <GlassCard className="border-sky-400/30 hover:border-sky-400/40 transition-colors duration-300">
          <div className="flex items-center gap-3 mb-5 pb-4 border-b border-slate-700/50">
            <div className="flex items-center justify-center w-10 h-10 bg-sky-400/10 rounded-xl border border-sky-400/30 shadow-lg shadow-sky-500/10">
              <Route className="w-5 h-5 text-sky-400" />
            </div>
            <div>
              <h4 className="text-base font-bold text-slate-100">Recommended Route</h4>
              <p className="text-xs text-slate-500 font-mono mt-0.5">AI-optimized path suggestion</p>
            </div>
          </div>
          <div className="p-5 bg-sky-400/5 border border-sky-400/30 rounded-xl hover:bg-sky-400/10 transition-colors duration-300">
            <p className="text-sm text-slate-200 leading-relaxed font-medium">{riskData.route_suggestion}</p>
          </div>
        </GlassCard>
      </motion.div>
    </div>
  )
}