import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Target, ShieldAlert, BatteryCharging, Wrench, Activity, ChevronRight, Zap, Radio } from 'lucide-react'
import api from '../lib/api.js'
import KPICard from '../components/KPICard'
import GlassCard from '../components/bits/GlassCard'
import CommandInput from '../components/bits/CommandInput'

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
    transition: { duration: 0.4, ease: 'easeOut' }
  }
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/dashboard').then(res => setData(res.data)).catch(err => console.error(err)).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 mx-auto mb-4 rounded-full border-2 border-sky-400/30 border-t-sky-400 animate-spin" />
          <p className="text-slate-300 font-medium text-lg">Initializing Mission Control...</p>
          <p className="text-slate-500 text-sm mt-2">Establishing secure connection</p>
        </motion.div>
      </div>
    )
  }
  
  if (!data) {
    return (
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-20"
      >
        <Radio className="w-16 h-16 mx-auto mb-4 text-red-400/50" />
        <p className="text-red-400 font-medium text-lg">Command Center Offline</p>
        <p className="text-slate-500 text-sm mt-2">Unable to establish backend connection</p>
      </motion.div>
    )
  }

  return (
    <motion.div 
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-8"
    >
      {/* Premium System Status Header */}
      <motion.div variants={itemVariants}>
        <GlassCard className="border-sky-400/20 hover:border-sky-400/40 transition-all duration-300" hover={false}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-14 h-14 bg-gradient-to-br from-sky-400/20 to-sky-600/20 rounded-xl border border-sky-400/30 overflow-hidden">
                <Zap className="w-7 h-7 text-sky-400 relative z-10" />
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-50 mb-1 tracking-tight">Mission Command Center</h2>
                <p className="text-sm text-slate-400">Real-time tactical intelligence & operations dashboard</p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 text-green-400 mb-1">
                <motion.div 
                  className="w-2.5 h-2.5 bg-green-400 rounded-full"
                  animate={{ 
                    opacity: [1, 0.3, 1],
                    scale: [1, 0.8, 1]
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <span className="text-sm font-mono font-bold">SYSTEMS NOMINAL</span>
              </div>
              <p className="text-xs text-slate-500 font-mono">UPLINK: {new Date().toLocaleTimeString()}</p>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* KPI Cards Grid with Connection Lines */}
      <motion.div variants={itemVariants} className="relative">
        {/* Animated connection beams */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <linearGradient id="beamGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgba(56, 189, 248, 0)" />
                <stop offset="50%" stopColor="rgba(56, 189, 248, 0.3)" />
                <stop offset="100%" stopColor="rgba(56, 189, 248, 0)" />
              </linearGradient>
            </defs>
            {/* Horizontal connection lines */}
            <motion.line
              x1="12.5" y1="50" x2="37.5" y2="50"
              stroke="url(#beamGradient)" strokeWidth="0.3"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 1, duration: 0.8, ease: "easeOut" }}
            />
            <motion.line
              x1="37.5" y1="50" x2="62.5" y2="50"
              stroke="url(#beamGradient)" strokeWidth="0.3"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 1.2, duration: 0.8, ease: "easeOut" }}
            />
            <motion.line
              x1="62.5" y1="50" x2="87.5" y2="50"
              stroke="url(#beamGradient)" strokeWidth="0.3"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 1.4, duration: 0.8, ease: "easeOut" }}
            />
          </svg>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10">
          <KPICard 
            title="Active Missions" 
            value={data.active_missions || 0} 
            subtitle={`of ${data.total_missions || 0} total operations`} 
            icon={Target} 
            color="sky" 
            delay={0.2}
          />
          <KPICard 
            title="Overall Risk" 
            value={data.overall_risk_score || 0} 
            suffix="/100" 
            subtitle={data.overall_risk_category || 'Calculating...'} 
            icon={ShieldAlert} 
            color="amber" 
            delay={0.3}
          />
          <KPICard 
            title="Fleet Health" 
            value={data.fleet_health_pct || 0} 
            suffix="%" 
            subtitle={`${data.total_assets || 0} assets deployed`} 
            icon={BatteryCharging} 
            color="green" 
            delay={0.4}
          />
          <KPICard 
            title="Maintenance Alert" 
            value={data.assets_needing_maintenance || 0} 
            subtitle="assets require service" 
            icon={Wrench} 
            color="red" 
            delay={0.5}
          />
        </div>
      </motion.div>

      {/* Enhanced Recent Missions Table */}
      <motion.div variants={itemVariants}>
        <GlassCard className="overflow-hidden p-0">
          {/* Table Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-slate-700/50 bg-slate-800/30">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-9 h-9 bg-sky-400/10 rounded-lg border border-sky-400/20">
                <Activity className="w-5 h-5 text-sky-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-100">Recent Mission Operations</h3>
                <p className="text-xs text-slate-500 font-mono mt-0.5">Live tactical feed</p>
              </div>
            </div>
            <div className="px-3 py-1.5 bg-sky-400/10 border border-sky-400/20 rounded-lg">
              <span className="text-xs text-sky-400 font-mono font-bold">
                {data.recent_missions?.length || 0} ACTIVE
              </span>
            </div>
          </div>

          {/* Table Content */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700/30 bg-slate-800/20">
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">Mission ID</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">Risk</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">Success Rate</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4"></th>
                </tr>
              </thead>
              <tbody>
                {data.recent_missions?.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center">
                      <Target className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                      <p className="text-slate-500 font-medium">No active missions</p>
                      <p className="text-slate-600 text-sm mt-1">Deploy your first operation to begin</p>
                    </td>
                  </tr>
                ) : (
                  data.recent_missions?.map((m, idx) => (
                    <motion.tr 
                      key={m.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 + idx * 0.05, duration: 0.3 }}
                      className="text-sm border-b border-slate-700/20 hover:bg-slate-700/30 transition-all duration-300 group cursor-pointer hover:shadow-[0_0_20px_rgba(56,189,248,0.1)]"
                    >
                      <td className="px-6 py-4 font-bold text-slate-100 group-hover:text-sky-400 transition-colors font-mono">
                        {m.name}
                      </td>
                      <td className="px-6 py-4 text-slate-300 font-medium capitalize">
                        {m.mission_type}
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-400/10 text-amber-400 border border-amber-400/30">
                          {m.risk_score?.toFixed(0)}/100
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-400/10 text-green-400 border border-green-400/30">
                          {m.success_probability?.toFixed(0)}%
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-sky-400/10 text-sky-400 border border-sky-400/30 uppercase">
                          {m.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-sky-400 group-hover:translate-x-1 transition-all duration-200" />
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </motion.div>

      {/* Natural Language Commander */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-1 h-6 bg-gradient-to-b from-sky-400 to-violet-400 rounded-full" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Natural Language Commander</h3>
        </div>
        <CommandInput />
      </motion.div>
    </motion.div>
  )
}