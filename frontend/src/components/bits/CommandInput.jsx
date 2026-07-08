import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Terminal, CornerDownLeft } from 'lucide-react'
import axios from 'axios'

const API = 'http://localhost:8000/api'

export default function CommandInput({ onCommandSuccess }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return
    setLoading(true)
    setResponse(null)
    try {
      const res = await axios.post(`${API}/commander`, { command: input })
      setResponse({ success: true, message: `Mission "${res.data.mission_name}" created successfully.` })
      if (onCommandSuccess) onCommandSuccess(res.data)
    } catch (err) {
      setResponse({ success: false, message: 'Failed to process command.' })
    } finally {
      setLoading(false)
      setInput('')
    }
  }

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-1 backdrop-blur-sm">
      <div className="flex items-center gap-2 bg-slate-900/60 rounded-xl px-4 py-2">
        <Terminal className="w-4 h-4 text-green-400 flex-shrink-0" />
        <span className="text-green-400 font-mono text-sm">anvikshaka:~$</span>
        <form onSubmit={handleSubmit} className="flex-1 flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter command... (e.g., 'Plan coastal mission 3 drones high threat')"
            className="flex-1 bg-transparent text-slate-200 font-mono text-sm placeholder-slate-600 focus:outline-none border-none"
            disabled={loading}
          />
          {loading ? (
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }} className="w-4 h-4 border-2 border-green-400/30 border-t-green-400 rounded-full" />
          ) : (
            <button type="submit" className="text-slate-500 hover:text-green-400 transition">
              <CornerDownLeft className="w-4 h-4" />
            </button>
          )}
        </form>
      </div>
      {response && (
        <div className={`px-4 py-2 text-xs font-mono ${response.success ? 'text-green-400' : 'text-red-400'}`}>
          {response.message}
        </div>
      )}
    </div>
  )
}