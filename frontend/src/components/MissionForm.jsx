import { useState } from 'react'
import { Rocket, ChevronRight, Shield, Plane, Ship, Clock } from 'lucide-react'

export default function MissionForm({ onSubmit, loading, error }) {
  const [form, setForm] = useState({
    name: 'Operation Sea Watch',
    mission_type: 'Coastal Surveillance',
    num_drones: 3,
    num_auvs: 2,
    duration_hours: 12,
    threat_level: 'medium',
    weather: 'moderate',
  })

  const handleChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }))
  const handleSubmit = (e) => { 
    e.preventDefault()
    if (!loading) {
      onSubmit(form)
    }
  }

  // Threat level colors
  const threatColors = {
    low: 'text-green-400 bg-green-400/10 border-green-400/30',
    medium: 'text-amber-400 bg-amber-400/10 border-amber-400/30',
    high: 'text-red-400 bg-red-400/10 border-red-400/30'
  }

  // Weather colors
  const weatherColors = {
    calm: 'text-green-400 bg-green-400/10 border-green-400/30',
    moderate: 'text-sky-400 bg-sky-400/10 border-sky-400/30',
    severe: 'text-red-400 bg-red-400/10 border-red-400/30'
  }

  const totalAssets = form.num_drones + form.num_auvs

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-slate-700/50">
        <div className="w-1 h-6 bg-gradient-to-b from-sky-400 to-violet-400 rounded-full" />
        <div className="flex-1">
          <h3 className="text-base font-bold text-slate-100">Mission Parameters</h3>
          <p className="text-xs text-slate-500 mt-0.5">Configure tactical deployment settings</p>
        </div>
        {totalAssets > 0 && (
          <div className="px-2.5 py-1 bg-sky-400/10 border border-sky-400/20 rounded-lg">
            <span className="text-xs text-sky-400 font-mono font-bold">{totalAssets} ASSETS</span>
          </div>
        )}
      </div>

      {/* Mission Designation */}
      <div>
        <label className="block text-xs font-mono text-slate-400 mb-2 uppercase tracking-wider font-semibold">
          Mission Designation
        </label>
        <input 
          type="text" 
          value={form.name} 
          onChange={(e) => handleChange('name', e.target.value)}
          disabled={loading}
          className="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-sm text-slate-100 font-mono
                     focus:outline-none focus:border-sky-400/60 focus:ring-2 focus:ring-sky-400/20 
                     hover:border-slate-600/50 transition-all duration-200
                     disabled:opacity-50 disabled:cursor-not-allowed" 
        />
      </div>

      {/* Mission Type */}
      <div>
        <label className="block text-xs font-mono text-slate-400 mb-2 uppercase tracking-wider font-semibold">
          Mission Type
        </label>
        <select 
          value={form.mission_type} 
          onChange={(e) => handleChange('mission_type', e.target.value)}
          disabled={loading}
          className="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-sm text-slate-200
                     focus:outline-none focus:border-sky-400/60 focus:ring-2 focus:ring-sky-400/20
                     hover:border-slate-600/50 transition-all duration-200 cursor-pointer
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <option>Coastal Surveillance</option>
          <option>Deep Sea Patrol</option>
          <option>Air Patrol</option>
          <option>Anti-Submarine</option>
        </select>
      </div>

      {/* Asset Deployment */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Plane className="w-4 h-4 text-sky-400" />
          <label className="text-xs font-mono text-slate-400 uppercase tracking-wider font-semibold">
            Asset Deployment
          </label>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-slate-500 mb-2 font-medium">Drones</label>
            <input 
              type="number" 
              min="0" 
              max="10" 
              value={form.num_drones} 
              onChange={(e) => handleChange('num_drones', parseInt(e.target.value) || 0)}
              disabled={loading}
              className="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-sm text-slate-200 font-mono
                         focus:outline-none focus:border-sky-400/60 focus:ring-2 focus:ring-sky-400/20
                         hover:border-slate-600/50 transition-all duration-200
                         disabled:opacity-50 disabled:cursor-not-allowed" 
            />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-2 font-medium">AUVs</label>
            <input 
              type="number" 
              min="0" 
              max="5" 
              value={form.num_auvs} 
              onChange={(e) => handleChange('num_auvs', parseInt(e.target.value) || 0)}
              disabled={loading}
              className="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-sm text-slate-200 font-mono
                         focus:outline-none focus:border-sky-400/60 focus:ring-2 focus:ring-sky-400/20
                         hover:border-slate-600/50 transition-all duration-200
                         disabled:opacity-50 disabled:cursor-not-allowed" 
            />
          </div>
        </div>
      </div>

      {/* Duration */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-4 h-4 text-sky-400" />
          <label className="text-xs font-mono text-slate-400 uppercase tracking-wider font-semibold">
            Operation Duration
          </label>
        </div>
        <div className="flex items-center gap-3">
          <input 
            type="number" 
            min="1" 
            max="72" 
            value={form.duration_hours} 
            onChange={(e) => handleChange('duration_hours', parseInt(e.target.value) || 1)}
            disabled={loading}
            className="flex-1 bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-2.5 text-sm text-slate-200 font-mono
                       focus:outline-none focus:border-sky-400/60 focus:ring-2 focus:ring-sky-400/20
                       hover:border-slate-600/50 transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed" 
          />
          <span className="text-sm text-slate-500 font-medium">hours</span>
        </div>
      </div>

      {/* Environmental Conditions */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-4 h-4 text-amber-400" />
          <label className="text-xs font-mono text-slate-400 uppercase tracking-wider font-semibold">
            Environmental Conditions
          </label>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-slate-500 mb-2 font-medium">Threat Level</label>
            <div className="relative">
              <select 
                value={form.threat_level} 
                onChange={(e) => handleChange('threat_level', e.target.value)}
                disabled={loading}
                className="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-2.5 pr-20 text-sm text-slate-200 capitalize
                           focus:outline-none focus:border-sky-400/60 focus:ring-2 focus:ring-sky-400/20
                           hover:border-slate-600/50 transition-all duration-200 cursor-pointer
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              <div className={`absolute right-3 top-1/2 -translate-y-1/2 px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${threatColors[form.threat_level]} pointer-events-none`}>
                {form.threat_level}
              </div>
            </div>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-2 font-medium">Weather</label>
            <div className="relative">
              <select 
                value={form.weather} 
                onChange={(e) => handleChange('weather', e.target.value)}
                disabled={loading}
                className="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-2.5 pr-24 text-sm text-slate-200 capitalize
                           focus:outline-none focus:border-sky-400/60 focus:ring-2 focus:ring-sky-400/20
                           hover:border-slate-600/50 transition-all duration-200 cursor-pointer
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="calm">Calm</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
              <div className={`absolute right-3 top-1/2 -translate-y-1/2 px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${weatherColors[form.weather]} pointer-events-none`}>
                {form.weather}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-3 bg-red-400/10 border border-red-400/30 rounded-lg">
          <p className="text-xs text-red-400 font-medium">{error}</p>
        </div>
      )}

      {/* Submit Button */}
      <button 
        type="submit" 
        disabled={loading}
        className="w-full bg-gradient-to-r from-sky-500 to-sky-600 text-white font-bold py-3.5 rounded-xl 
                   flex items-center justify-center gap-2 
                   hover:from-sky-400 hover:to-sky-500 
                   transition-all duration-200 shadow-lg shadow-sky-500/20
                   disabled:opacity-50 disabled:cursor-not-allowed disabled:from-slate-600 disabled:to-slate-700 disabled:shadow-none"
      >
        {loading ? (
          <>
            <Ship className="w-5 h-5 animate-spin" />
            <span>Processing Mission...</span>
          </>
        ) : (
          <>
            <Rocket className="w-5 h-5" />
            <span>Launch Mission</span>
            <ChevronRight className="w-4 h-4" />
          </>
        )}
      </button>
    </form>
  )
}