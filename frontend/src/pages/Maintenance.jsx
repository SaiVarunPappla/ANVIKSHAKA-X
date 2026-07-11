import { useState } from 'react'
import { motion } from 'framer-motion'
import { Wrench, RefreshCw, Zap, AlertTriangle, CheckCircle2 } from 'lucide-react'
import api from '../lib/api'
import MaintenanceTable from '../components/MaintenanceTable'
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

export default function Maintenance() {
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const runPrediction = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/maintenance', { asset_ids: null })
      setPredictions(res.data)
    } catch (err) {
      setError('Failed to run maintenance prediction')
    } finally { 
      setLoading(false) 
    }
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
        <GlassCard className="border-red-400/20 hover:border-red-400/30" hover={false}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-12 h-12 bg-gradient-to-br from-red-400/20 to-orange-400/20 rounded-xl border border-red-400/30 shadow-lg shadow-red-500/10">
                <Wrench className="w-6 h-6 text-red-400" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-red-400/5 to-transparent pointer-events-none" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-50 tracking-tight mb-1">Predictive Maintenance Centre</h2>
                <p className="text-sm text-slate-400">AI-powered asset failure prediction & scheduling</p>
              </div>
            </div>
            <button 
              onClick={runPrediction}
              disabled={loading}
              className="group flex items-center gap-2.5 px-5 py-3 bg-gradient-to-r from-sky-500 to-sky-400 hover:from-sky-400 hover:to-sky-300 
                         text-white rounded-xl text-sm font-bold shadow-lg shadow-sky-500/30 hover:shadow-sky-500/50
                         transition-all duration-300 transform hover:scale-105
                         disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:from-slate-600 disabled:to-slate-600 disabled:hover:scale-100 disabled:shadow-none
                         focus:outline-none focus:ring-2 focus:ring-sky-400/50 focus-visible:ring-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
              {loading ? 'Analyzing...' : 'Run Analysis'}
            </button>
          </div>
        </GlassCard>
      </motion.div>

      {/* Status Indicators */}
      {predictions && !loading && (
        <motion.div variants={itemVariants}>
          <GlassCard className="border-green-400/30 bg-green-400/10 hover:border-green-400/40 shadow-lg shadow-green-500/10" hover={false}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 bg-green-400/20 rounded-xl border border-green-400/30">
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <p className="text-sm font-bold text-green-400">Analysis Complete</p>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">{predictions.length} assets evaluated • Ready for review</p>
                </div>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-400/10 border border-green-400/30 rounded-lg">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="text-xs text-green-400 font-mono font-bold">ACTIVE</span>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Error Display */}
      {error && !loading && (
        <motion.div variants={itemVariants}>
          <GlassCard className="border-red-400/40 bg-red-400/10 hover:border-red-400/50" hover={false}>
            <div className="flex items-center gap-4">
              <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-bold text-red-400 mb-1">{error}</p>
                <p className="text-xs text-slate-400">Verify backend connection and try again</p>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Content Area */}
      {loading ? (
        <motion.div variants={itemVariants}>
          <GlassCard className="p-16 text-center border-sky-400/20 hover:border-sky-400/30" hover={false}>
            <div className="flex flex-col items-center">
              <div className="relative mb-6">
                <div className="w-20 h-20 rounded-full border-2 border-sky-400/30 border-t-sky-400 animate-spin" />
                <Wrench className="w-9 h-9 text-sky-400 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <h3 className="text-lg font-bold text-slate-100 mb-2">Running Predictive Analysis</h3>
              <p className="text-sm text-slate-400 mb-4">Evaluating asset health and failure probability...</p>
              <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                <div className="w-1.5 h-1.5 bg-sky-400 rounded-full animate-pulse" />
                Processing ML predictions
              </div>
            </div>
          </GlassCard>
        </motion.div>
      ) : (
        <motion.div variants={itemVariants}>
          <GlassCard className="p-0 overflow-hidden">
            <MaintenanceTable predictions={predictions} />
          </GlassCard>
        </motion.div>
      )}
    </motion.div>
  )
}