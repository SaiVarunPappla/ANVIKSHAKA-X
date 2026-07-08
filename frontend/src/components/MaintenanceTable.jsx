import React from 'react'
import { motion } from 'framer-motion'
import { Wrench, AlertCircle } from 'lucide-react'

const rowVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: (i) => ({
    opacity: 1,
    x: 0,
    transition: {
      delay: i * 0.08,
      duration: 0.3,
      ease: 'easeOut'
    }
  })
}

export default function MaintenanceTable({ predictions }) {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="p-16 text-center">
        <AlertCircle className="w-16 h-16 mx-auto mb-4 text-slate-600" />
        <h3 className="text-lg font-bold text-slate-300 mb-2">No Maintenance Data</h3>
        <p className="text-sm text-slate-500">Click "Run Analysis" to generate predictions</p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden">
      {/* Table Header */}
      <div className="bg-slate-900/60 border-b border-slate-700/50 px-6 py-4">
        <div className="flex items-center gap-3 mb-1">
          <Wrench className="w-4 h-4 text-slate-400" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Asset Health Analysis</h3>
        </div>
        <p className="text-xs text-slate-500 font-mono">{predictions.length} assets monitored</p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700/50 bg-slate-900/40">
              <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-widest">Asset Name</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-widest">Type</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-widest">Failure Probability</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-slate-300 uppercase tracking-widest">Risk Level</th>
            </tr>
          </thead>
          <tbody>
            {predictions.map((pred, idx) => {
              const failurePercent = (pred.failure_probability * 100).toFixed(0)
              const isCritical = pred.risk_level === 'critical'
              const isHigh = pred.risk_level === 'high'
              
              return (
                <motion.tr
                  key={idx}
                  custom={idx}
                  variants={rowVariants}
                  initial="hidden"
                  animate="visible"
                  className="group border-b border-slate-700/30 hover:bg-slate-700/20 hover:border-slate-600/50 transition-all duration-300 cursor-pointer"
                >
                  <td className="px-6 py-4 text-sm font-bold text-slate-100 group-hover:text-white transition-colors">
                    {pred.asset_name}
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-xs text-slate-400 uppercase font-mono tracking-wide font-semibold">
                      {pred.asset_type}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      {/* Progress Bar */}
                      <div className="relative flex-1 max-w-[160px] h-3 bg-slate-900/80 rounded-full overflow-hidden border border-slate-700/50 shadow-inner">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${failurePercent}%` }}
                          transition={{ delay: idx * 0.08 + 0.3, duration: 0.8, ease: 'easeOut' }}
                          className={`h-full rounded-full relative overflow-hidden ${
                            isCritical 
                              ? 'bg-gradient-to-r from-red-600 to-red-500' 
                              : isHigh 
                              ? 'bg-gradient-to-r from-orange-500 to-orange-400' 
                              : 'bg-gradient-to-r from-green-500 to-green-400'
                          }`}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
                        </motion.div>
                      </div>
                      {/* Percentage */}
                      <span className={`text-sm font-bold font-mono tabular-nums min-w-[45px] ${
                        isCritical ? 'text-red-400' : isHigh ? 'text-orange-400' : 'text-green-400'
                      }`}>
                        {failurePercent}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-black uppercase tracking-wider border-2 transition-all duration-200 group-hover:scale-105 ${
                      isCritical 
                        ? 'bg-red-500/20 text-red-400 border-red-500/50 shadow-lg shadow-red-500/20' 
                        : isHigh
                        ? 'bg-orange-500/20 text-orange-400 border-orange-500/50 shadow-lg shadow-orange-500/20'
                        : 'bg-green-500/20 text-green-400 border-green-500/50 shadow-lg shadow-green-500/20'
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full mr-2 ${
                        isCritical ? 'bg-red-400' : isHigh ? 'bg-orange-400' : 'bg-green-400'
                      } ${isCritical || isHigh ? 'animate-pulse' : ''}`} />
                      {pred.risk_level}
                    </span>
                  </td>
                </motion.tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}