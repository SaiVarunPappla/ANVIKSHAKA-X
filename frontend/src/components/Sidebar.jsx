import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Target, ShieldAlert, Wrench, BarChart3, MessageSquare } from 'lucide-react'
import { motion } from 'framer-motion'
import RadarScan from './bits/RadarScan'
import PulseRing from './bits/PulseRing'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/mission-planner', label: 'Mission Planner', icon: Target },
  { to: '/risk', label: 'Risk Analysis', icon: ShieldAlert },
  { to: '/maintenance', label: 'Maintenance', icon: Wrench },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/chat', label: 'ANVIKSHA AI', icon: MessageSquare },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-800/50 backdrop-blur-xl border-r border-slate-700/60 z-50 flex flex-col shadow-[4px_0_24px_rgba(0,0,0,0.4)]">
      {/* Header */}
      <div className="px-6 py-6 border-b border-slate-700/60 flex items-center gap-3 bg-slate-800/30">
        <RadarScan size={40} />
        <div>
          <h1 className="text-lg font-extrabold text-slate-50 tracking-tight">ANVIKSHAKA</h1>
          <p className="text-[10px] font-mono text-sky-400 tracking-widest">X · MISSION INTEL</p>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item, idx) => (
          <NavLink 
            key={item.to} 
            to={item.to} 
            end={item.to === '/'}
          >
            {({ isActive }) => (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05, duration: 0.3 }}
                className={`
                  relative flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium
                  transition-all duration-250 group
                  ${isActive 
                    ? 'bg-sky-400/10 text-sky-400 border border-sky-400/30' 
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-700/30 border border-transparent'
                  }
                `}
              >
                {/* Active glow */}
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="absolute inset-0 rounded-xl shadow-[0_0_20px_rgba(56,189,248,0.2)]"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                
                {/* Content */}
                <item.icon className={`w-5 h-5 relative z-10 transition-transform duration-250 ${!isActive && 'group-hover:scale-110'}`} />
                <span className="relative z-10">{item.label}</span>
              </motion.div>
            )}
          </NavLink>
        ))}
      </nav>
      
      {/* Footer */}
      <div className="px-6 py-4 border-t border-slate-700/60 flex items-center gap-3 bg-slate-800/30">
        <PulseRing size={20} color="#22c55e" />
        <span className="text-xs font-mono text-slate-400">SYSTEM ONLINE</span>
      </div>
    </aside>
  )
}