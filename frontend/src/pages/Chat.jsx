import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Send, User, Cpu, Zap, MessageSquare } from 'lucide-react'
import api from '../lib/api.js'
import GlassCard from '../components/bits/GlassCard'
import RadarScan from '../components/bits/RadarScan'
import TypewriterText from '../components/bits/TypewriterText'

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

const messageVariants = {
  hidden: { opacity: 0, y: 10, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.3,
      ease: 'easeOut'
    }
  }
}

export default function Chat() {
  const [messages, setMessages] = useState([{ id: 1, role: 'ai', text: "ANVIKSHA online. How can I assist, Commander?" }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiStatus, setAiStatus] = useState({ online: false, provider: 'unknown', checking: true, fallback_reason: null })
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Check AI status on mount
  useEffect(() => {
    const checkAiStatus = async () => {
      try {
        const res = await api.get('/health')
        setAiStatus({
          online: res.data.ai_available || false,
          provider: res.data.ai_provider || 'unknown',
          checking: false,
          fallback_reason: res.data.ai_available ? null : 'AI not configured'
        })
      } catch (err) {
        setAiStatus({ online: false, provider: 'error', checking: false, fallback_reason: 'Connection error' })
      }
    }
    checkAiStatus()
  }, [])

  const sendMessage = async (text) => {
    if (!text.trim()) return
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text }])
    setInput('')
    setLoading(true)
    try {
      const res = await api.post('/chat', { message: text })
      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'ai', text: res.data.response }])
      
      // Update AI status from response metadata
      if (res.data.ai_powered !== undefined) {
        setAiStatus(prev => ({
          ...prev,
          online: res.data.ai_powered,
          provider: res.data.provider || res.data.model || prev.provider,
          fallback_reason: res.data.fallback_reason || null
        }))
      }
    } catch (err) {
      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'ai', text: "Connection error." }])
      setAiStatus(prev => ({ ...prev, online: false, fallback_reason: "Connection error" }))
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
        <GlassCard className="border-purple-400/20 hover:border-purple-400/30" hover={false}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-12 h-12 bg-gradient-to-br from-purple-400/20 to-violet-400/20 rounded-xl border border-purple-400/30 shadow-lg shadow-purple-500/10">
                <Cpu className="w-6 h-6 text-purple-400" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-purple-400/5 to-transparent pointer-events-none" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-50 tracking-tight mb-1">AI Command Assistant</h2>
                <p className="text-sm text-slate-400">Natural language mission intelligence interface</p>
              </div>
            </div>
            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg shadow-lg ${
              aiStatus.checking 
                ? 'bg-slate-400/10 border border-slate-400/30 shadow-slate-500/10' 
                : aiStatus.online 
                  ? 'bg-green-400/10 border border-green-400/30 shadow-green-500/10' 
                  : 'bg-amber-400/10 border border-amber-400/30 shadow-amber-500/10'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                aiStatus.checking 
                  ? 'bg-slate-400 animate-pulse' 
                  : aiStatus.online 
                    ? 'bg-green-400 animate-pulse' 
                    : 'bg-amber-400'
              }`} />
              <span className={`text-xs font-mono font-bold tracking-wider ${
                aiStatus.checking 
                  ? 'text-slate-400' 
                  : aiStatus.online 
                    ? 'text-green-400' 
                    : 'text-amber-400'
              }`}>
                {aiStatus.checking ? 'CHECKING' : aiStatus.online ? 'AI ONLINE' : 'LIMITED MODE'}
              </span>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Chat Interface */}
      <motion.div 
        variants={itemVariants}
        className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-16rem)]"
      >
        <div className="lg:col-span-2 flex flex-col h-full">
          <GlassCard className="flex-1 flex flex-col overflow-hidden p-0 border-purple-400/20">
            {/* Chat Header */}
            <div className="px-6 py-4 border-b border-slate-700/50 flex items-center gap-3 bg-slate-900/40">
              <div className="flex items-center justify-center w-10 h-10 bg-purple-400/10 rounded-xl border border-purple-400/30">
                <RadarScan size={24} />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-slate-100">ANVIKSHA</h3>
                <p className="text-xs text-slate-500 font-mono">
                  {aiStatus.online ? `AI Strategic Advisor • ${aiStatus.provider}` : 'AI Strategic Advisor • Rule-based Mode'}
                </p>
              </div>
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg ${
                aiStatus.online 
                  ? 'bg-green-400/10 border border-green-400/30' 
                  : 'bg-amber-400/10 border border-amber-400/30'
              }`}>
                <div className={`w-1.5 h-1.5 rounded-full ${aiStatus.online ? 'bg-green-400' : 'bg-amber-400'}`} />
                <span className={`text-xs font-mono font-semibold ${aiStatus.online ? 'text-green-400' : 'text-amber-400'}`}>
                  {aiStatus.online ? 'Active' : 'Limited'}
                </span>
              </div>
            </div>
            
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar bg-gradient-to-b from-slate-900/20 to-transparent">
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  variants={messageVariants}
                  initial="hidden"
                  animate="visible"
                  className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center border shadow-lg ${
                    msg.role === 'user' 
                      ? 'bg-gradient-to-br from-sky-400/20 to-sky-600/10 border-sky-400/30 shadow-sky-500/20' 
                      : 'bg-gradient-to-br from-purple-400/20 to-purple-600/10 border-purple-400/30 shadow-purple-500/20'
                  }`}>
                    {msg.role === 'user' ? (
                      <User className="w-5 h-5 text-sky-400" />
                    ) : (
                      <RadarScan size={22} />
                    )}
                  </div>
                  
                  {/* Message Bubble */}
                  <div className={`max-w-[80%] px-5 py-3 rounded-2xl shadow-lg transition-all duration-200 ${
                    msg.role === 'user' 
                      ? 'bg-gradient-to-br from-sky-400/15 to-sky-600/10 text-slate-100 border border-sky-400/30 hover:border-sky-400/50' 
                      : 'bg-slate-800/80 text-slate-200 border border-slate-700/50 hover:border-purple-400/30'
                  }`}>
                    {msg.role === 'ai' ? (
                      <TypewriterText text={msg.text} speed={20} />
                    ) : (
                      <p className="text-sm leading-relaxed">{msg.text}</p>
                    )}
                  </div>
                </motion.div>
              ))}
              
              {/* Loading Indicator */}
              {loading && (
                <motion.div
                  variants={messageVariants}
                  initial="hidden"
                  animate="visible"
                  className="flex gap-3"
                >
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-br from-purple-400/20 to-purple-600/10 border border-purple-400/30 shadow-lg shadow-purple-500/20">
                    <RadarScan size={22} />
                  </div>
                  <div className="px-5 py-3 bg-slate-800/80 border border-slate-700/50 rounded-2xl">
                    <div className="flex items-center gap-2 text-slate-400">
                      <Zap className="w-4 h-4 text-purple-400 animate-pulse" />
                      <span className="text-sm font-medium">ANVIKSHA is processing...</span>
                      <div className="flex gap-1">
                        <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
            
            {/* Input Area */}
            <div className="p-5 border-t border-slate-700/50 flex gap-3 bg-slate-900/60">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage(input)}
                placeholder="Ask ANVIKSHA anything..."
                disabled={loading}
                className="flex-1 bg-slate-900/80 border border-slate-700/50 rounded-xl px-4 py-3 text-sm text-slate-200 
                           placeholder:text-slate-500 focus:outline-none focus:border-purple-400/60 focus:ring-2 focus:ring-purple-400/20
                           hover:border-slate-600/50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <button 
                onClick={() => sendMessage(input)} 
                disabled={loading || !input.trim()}
                className="group flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-r from-purple-500 to-purple-400 
                           text-white shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition-all duration-300 
                           transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                           focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus-visible:ring-2"
              >
                <Send className="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-200" />
              </button>
            </div>
          </GlassCard>
        </div>
        
        {/* Quick Actions Sidebar */}
        <GlassCard className="p-6 hidden lg:flex flex-col border-slate-700/50">
          <div className="flex items-center gap-3 mb-5 pb-4 border-b border-slate-700/50">
            <div className="flex items-center justify-center w-8 h-8 bg-purple-400/10 rounded-lg border border-purple-400/30">
              <MessageSquare className="w-4 h-4 text-purple-400" />
            </div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Quick Actions</h3>
          </div>
          <div className="flex flex-col gap-3">
            {["Explain risk score", "Which assets need maintenance?", "Summarize latest mission"].map(chip => (
              <button 
                key={chip} 
                onClick={() => sendMessage(chip)} 
                disabled={loading}
                className="group text-left px-4 py-3 bg-slate-800/60 hover:bg-slate-800/80 rounded-xl border border-slate-700/50 
                           hover:border-purple-400/40 text-slate-400 hover:text-purple-400 transition-all duration-200
                           disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-purple-400/30"
              >
                <p className="text-sm font-medium leading-relaxed">{chip}</p>
              </button>
            ))}
          </div>
        </GlassCard>
      </motion.div>
    </motion.div>
  )
}