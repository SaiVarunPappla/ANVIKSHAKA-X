import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'

// Number ticker animation component
function NumberTicker({ value, suffix = '' }) {
  const [displayValue, setDisplayValue] = useState(0)
  const prevValueRef = useRef(0)

  useEffect(() => {
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) {
      setDisplayValue(value)
      return
    }

    const startValue = prevValueRef.current
    const endValue = numValue
    const duration = 800
    const startTime = Date.now()

    const animate = () => {
      const now = Date.now()
      const progress = Math.min((now - startTime) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3) // easeOut cubic
      const current = startValue + (endValue - startValue) * eased
      
      setDisplayValue(current)
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        prevValueRef.current = endValue
      }
    }

    animate()
  }, [value])

  const formattedValue = typeof displayValue === 'number' 
    ? displayValue.toFixed(displayValue % 1 === 0 ? 0 : 1)
    : displayValue

  return (
    <>
      <span className="tabular-nums">{formattedValue}</span>
      {suffix && <span className="text-lg font-bold text-slate-500 ml-1">{suffix}</span>}
    </>
  )
}

export default function KPICard({ title, value, suffix = '', icon: Icon, color = 'blue', delay = 0, subtitle, label }) {
  const cardRef = useRef(null)
  const [isHovered, setIsHovered] = useState(false)
  
  // 3D tilt effect
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  
  const mouseXSpring = useSpring(x, { stiffness: 150, damping: 15 })
  const mouseYSpring = useSpring(y, { stiffness: 150, damping: 15 })
  
  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], [7, -7])
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], [-7, 7])

  const handleMouseMove = (e) => {
    if (!cardRef.current) return
    
    const rect = cardRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    
    x.set((e.clientX - centerX) / rect.width)
    y.set((e.clientY - centerY) / rect.height)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
    setIsHovered(false)
  }

  const colorMap = {
    blue: {
      text: 'text-sky-400',
      bg: 'bg-sky-400/10',
      border: 'border-sky-400/30',
      glow: 'shadow-[0_0_30px_rgba(56,189,248,0.4)]',
      iconBg: 'bg-gradient-to-br from-sky-400/20 to-sky-600/20'
    },
    sky: {
      text: 'text-sky-400',
      bg: 'bg-sky-400/10',
      border: 'border-sky-400/30',
      glow: 'shadow-[0_0_30px_rgba(56,189,248,0.4)]',
      iconBg: 'bg-gradient-to-br from-sky-400/20 to-sky-600/20'
    },
    green: {
      text: 'text-green-400',
      bg: 'bg-green-400/10',
      border: 'border-green-400/30',
      glow: 'shadow-[0_0_30px_rgba(34,197,94,0.4)]',
      iconBg: 'bg-gradient-to-br from-green-400/20 to-green-600/20'
    },
    amber: {
      text: 'text-amber-400',
      bg: 'bg-amber-400/10',
      border: 'border-amber-400/30',
      glow: 'shadow-[0_0_30px_rgba(251,191,36,0.4)]',
      iconBg: 'bg-gradient-to-br from-amber-400/20 to-amber-600/20'
    },
    violet: {
      text: 'text-violet-400',
      bg: 'bg-violet-400/10',
      border: 'border-violet-400/30',
      glow: 'shadow-[0_0_30px_rgba(167,139,250,0.4)]',
      iconBg: 'bg-gradient-to-br from-violet-400/20 to-violet-600/20'
    },
    red: {
      text: 'text-red-400',
      bg: 'bg-red-400/10',
      border: 'border-red-400/30',
      glow: 'shadow-[0_0_30px_rgba(248,113,113,0.4)]',
      iconBg: 'bg-gradient-to-br from-red-400/20 to-red-600/20'
    }
  }
  
  const colors = colorMap[color] || colorMap.sky
  const displayTitle = label || title

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, delay, ease: 'easeOut' }}
      style={{
        rotateX,
        rotateY,
        transformStyle: 'preserve-3d'
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      className={`relative p-6 rounded-2xl border backdrop-blur-xl transition-all duration-300 cursor-pointer group ${colors.bg} ${colors.border} ${
        isHovered ? colors.glow : ''
      }`}
    >
      {/* Shine effect on hover */}
      <motion.div
        className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
        style={{ transform: 'translateZ(1px)' }}
      />
      
      {/* Animated border glow */}
      {isHovered && (
        <motion.div
          className={`absolute inset-0 rounded-2xl ${colors.border} blur-xl opacity-50`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.5 }}
          exit={{ opacity: 0 }}
        />
      )}

      <div className="relative" style={{ transform: 'translateZ(20px)' }}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-xs font-mono text-slate-400 tracking-wider uppercase font-medium">
              {displayTitle}
            </p>
            {subtitle && (
              <p className="text-[10px] text-slate-500 mt-1">{subtitle}</p>
            )}
          </div>
          {Icon && (
            <motion.div 
              className={`w-11 h-11 rounded-xl flex items-center justify-center border ${colors.iconBg} ${colors.border} ${colors.text} relative overflow-hidden`}
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ duration: 0.2 }}
            >
              <Icon className="w-5 h-5 relative z-10" />
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />
            </motion.div>
          )}
        </div>
        
        <div className="flex items-baseline gap-1">
          <motion.span 
            className={`text-3xl font-extrabold ${colors.text} font-mono`}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, delay: delay + 0.2 }}
          >
            <NumberTicker value={value} suffix={suffix} />
          </motion.span>
        </div>

        {/* Data pulse indicator */}
        <div className="absolute bottom-2 right-2 flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className={`w-1 h-1 rounded-full ${colors.bg} ${colors.border} border`}
              animate={{
                opacity: [0.3, 1, 0.3],
                scale: [0.8, 1, 0.8]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.2
              }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}