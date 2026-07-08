import { motion } from 'framer-motion'

export default function GlassCard({ children, className = '', delay = 0, hover = true, ...props }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
      whileHover={hover ? { y: -3, transition: { duration: 0.2 } } : {}}
      className={`relative rounded-2xl overflow-hidden group ${className}`}
      {...props}
    >
      {/* Glass surface with depth */}
      <div className="absolute inset-0 bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl" />
      
      {/* Inner highlight */}
      <div className="absolute inset-0 rounded-2xl shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]" />
      
      {/* Edge glow on hover */}
      {hover && (
        <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 shadow-[0_0_0_1px_rgba(56,189,248,0.2),0_0_20px_rgba(56,189,248,0.15)]" />
      )}
      
      {/* Depth shadow */}
      <div className="absolute inset-0 rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.3)]" />
      
      {/* Content */}
      <div className="relative z-10 p-5">{children}</div>
    </motion.div>
  )
}