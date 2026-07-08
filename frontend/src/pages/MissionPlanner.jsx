import { useState } from 'react'
import axios from 'axios'
import { Target, Cpu, AlertTriangle, Zap } from 'lucide-react'
import MissionForm from '../components/MissionForm'
import AgentOutputPanel from '../components/AgentOutputPanel'
import GlassCard from '../components/bits/GlassCard'
import RadarScan from '../components/bits/RadarScan'

const API = 'http://localhost:8000/api'

export default function MissionPlanner() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (formData) => {
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await axios.post(`${API}/mission`, formData)
      setResult(res.data)
    } catch (err) {
      setError('Failed to create mission. Check backend connection.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Premium Page Header */}
      <GlassCard className="border-sky-400/20" hover={false}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative flex items-center justify-center w-12 h-12 bg-gradient-to-br from-sky-400/20 to-violet-400/20 rounded-xl border border-sky-400/30">
              <Target className="w-6 h-6 text-sky-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-50 tracking-tight">Mission Planning Console</h2>
              <p className="text-sm text-slate-400">Configure assets & launch tactical operations</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-400/10 border border-green-400/20 rounded-lg">
            <div className="w-2 h-2 bg-green-400 rounded-full" />
            <span className="text-xs text-green-400 font-mono font-bold">READY</span>
          </div>
        </div>
      </GlassCard>

      {/* Two-column grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Form column */}
        <div className="lg:col-span-2">
          <GlassCard>
            <MissionForm onSubmit={handleSubmit} loading={loading} error={error} />
          </GlassCard>
        </div>

        {/* Output column */}
        <div className="lg:col-span-3">
          {loading ? (
            <GlassCard className="p-12 text-center h-full flex flex-col items-center justify-center border-sky-400/30" hover={false}>
              <div className="relative mb-6">
                <div className="w-16 h-16 rounded-full border-2 border-sky-400/30 border-t-sky-400 animate-spin" />
                <Cpu className="w-8 h-8 text-sky-400 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <h3 className="text-lg font-bold text-slate-200 mb-2">Mission Planning in Progress</h3>
              <p className="text-sm text-slate-400 mb-4">Agent intelligence systems processing tactical data...</p>
            </GlassCard>
          ) : !result ? (
            <GlassCard className="p-12 text-center h-full flex flex-col items-center justify-center" hover={false}>
              <div className="relative mb-6">
                <div className="absolute inset-0 bg-sky-400/10 rounded-full blur-xl" />
                <RadarScan size={80} className="relative" />
              </div>
              <h3 className="text-lg font-bold text-slate-300 mb-2">Agent Pipeline Standby</h3>
              <p className="text-sm text-slate-500 mb-4">Configure mission parameters and launch to activate agent intelligence analysis</p>
              <div className="flex items-center gap-2 text-xs text-slate-600">
                <Zap className="w-3 h-3" />
                <span className="font-mono">System ready for tactical deployment</span>
              </div>
            </GlassCard>
          ) : (
            <GlassCard className="border-green-400/20">
              <div className="flex items-center gap-3 mb-5 pb-4 border-b border-slate-700/50">
                <div className="flex items-center justify-center w-9 h-9 bg-green-400/10 rounded-lg border border-green-400/20">
                  <Cpu className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">Agent Intelligence Output</h3>
                  <p className="text-xs text-slate-500 font-mono mt-0.5">Multi-agent tactical analysis complete</p>
                </div>
              </div>
              <AgentOutputPanel agents={result.agents} supervisorBrief={result.supervisor_brief} />
            </GlassCard>
          )}

          {/* Error display */}
          {error && !loading && (
            <div className="mt-4">
              <GlassCard className="border-red-400/30 bg-red-400/5" hover={false}>
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-red-400">{error}</p>
                    <p className="text-xs text-slate-500 mt-1">Verify backend is running on localhost:8000</p>
                  </div>
                </div>
              </GlassCard>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}