import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, LineChart as LineChartIcon, TrendingUp, Activity, Database } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import axios from 'axios'
import GlassCard from '../components/bits/GlassCard'

const API = 'http://localhost:8000/api'

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

export default function Analytics() {
  const [missions, setMissions] = useState([])
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/missions`).then(res => setMissions(res.data)),
      axios.get(`${API}/assets`).then(res => setAssets(res.data))
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="w-12 h-12 mx-auto mb-4 rounded-full border-2 border-violet-400/30 border-t-violet-400 animate-spin" />
          <p className="text-slate-400 font-medium">Analyzing Fleet Data...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-8"
    >
      {/* Premium Page Header */}
      <motion.div variants={itemVariants}>
        <GlassCard className="border-violet-400/20 hover:border-violet-400/30" hover={false}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-12 h-12 bg-gradient-to-br from-violet-400/20 to-purple-400/20 rounded-xl border border-violet-400/30 shadow-lg shadow-violet-500/10">
                <BarChart3 className="w-6 h-6 text-violet-400" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-violet-400/5 to-transparent pointer-events-none" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-50 tracking-tight mb-1">Fleet Analytics</h2>
                <p className="text-sm text-slate-400">Real-time operational metrics & performance insights</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-violet-400/10 border border-violet-400/30 rounded-lg shadow-lg shadow-violet-500/10">
              <div className="w-2 h-2 bg-violet-400 rounded-full animate-pulse" />
              <span className="text-xs text-violet-400 font-mono font-bold tracking-wider">LIVE DATA</span>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Asset Battery Health Chart */}
        <motion.div variants={itemVariants}>
          <GlassCard className="border-green-400/20 hover:border-green-400/30 transition-colors duration-300">
            <div className="flex items-center justify-between mb-5 pb-4 border-b border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 bg-green-400/10 rounded-xl border border-green-400/30 shadow-lg shadow-green-500/10">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">Asset Battery Health</h3>
                  <p className="text-xs text-slate-500 font-mono mt-0.5">Power level monitoring</p>
                </div>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-400/10 border border-green-400/30 rounded-lg">
                <span className="text-xs font-bold text-green-400 font-mono">{assets.length} ASSETS</span>
              </div>
            </div>
            
            {assets.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <Database className="w-12 h-12 mb-3 text-slate-600" />
                <p className="text-sm font-medium text-slate-400">No Asset Data Available</p>
                <p className="text-xs text-slate-500 mt-1">Deploy assets to begin monitoring</p>
              </div>
            ) : (
              <div className="bg-slate-900/40 rounded-xl border border-slate-700/30 p-4">
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={assets}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                    <XAxis 
                      dataKey="name" 
                      tick={{ fill: '#94a3b8', fontSize: 11 }} 
                      stroke="#475569"
                    />
                    <YAxis 
                      tick={{ fill: '#94a3b8', fontSize: 11 }} 
                      domain={[0, 100]} 
                      stroke="#475569"
                    />
                    <Tooltip 
                      contentStyle={{ 
                        background: '#0f172a', 
                        border: '1px solid #475569',
                        borderRadius: '8px',
                        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)'
                      }}
                      labelStyle={{ color: '#cbd5e1', fontSize: 12, fontWeight: 600 }}
                      itemStyle={{ color: '#22c55e', fontSize: 12 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="battery_health" 
                      stroke="#22c55e" 
                      strokeWidth={3}
                      dot={{ fill: '#22c55e', r: 4 }}
                      activeDot={{ r: 6, fill: '#22c55e' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </GlassCard>
        </motion.div>

        {/* Mission Count by Type Chart */}
        <motion.div variants={itemVariants}>
          <GlassCard className="border-sky-400/20 hover:border-sky-400/30 transition-colors duration-300">
            <div className="flex items-center justify-between mb-5 pb-4 border-b border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 bg-sky-400/10 rounded-xl border border-sky-400/30 shadow-lg shadow-sky-500/10">
                  <Activity className="w-5 h-5 text-sky-400" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">Mission Distribution</h3>
                  <p className="text-xs text-slate-500 font-mono mt-0.5">Operations by type</p>
                </div>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-sky-400/10 border border-sky-400/30 rounded-lg">
                <span className="text-xs font-bold text-sky-400 font-mono">{missions.length} MISSIONS</span>
              </div>
            </div>
            
            {missions.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <Database className="w-12 h-12 mb-3 text-slate-600" />
                <p className="text-sm font-medium text-slate-400">No Mission Data Available</p>
                <p className="text-xs text-slate-500 mt-1">Create missions to view analytics</p>
              </div>
            ) : (
              <div className="bg-slate-900/40 rounded-xl border border-slate-700/30 p-4">
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={missions}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                    <XAxis 
                      dataKey="mission_type" 
                      tick={{ fill: '#94a3b8', fontSize: 11 }} 
                      stroke="#475569"
                    />
                    <YAxis 
                      tick={{ fill: '#94a3b8', fontSize: 11 }} 
                      stroke="#475569"
                    />
                    <Tooltip 
                      contentStyle={{ 
                        background: '#0f172a', 
                        border: '1px solid #475569',
                        borderRadius: '8px',
                        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)'
                      }}
                      labelStyle={{ color: '#cbd5e1', fontSize: 12, fontWeight: 600 }}
                      itemStyle={{ color: '#38bdf8', fontSize: 12 }}
                    />
                    <Bar 
                      dataKey="id" 
                      fill="#38bdf8" 
                      radius={[6, 6, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </GlassCard>
        </motion.div>
      </div>
    </motion.div>
  )
}