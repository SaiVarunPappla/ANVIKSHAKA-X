import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, CheckCircle2, Terminal } from 'lucide-react'

export default function AgentOutputPanel({ agents, supervisorBrief }) {
  const agentEntries = Object.entries(agents || {})
  return (
    <div className="space-y-3">
      {agentEntries.map(([name, output], idx) => (
        <AgentCard key={name} agentName={name} output={output} index={idx} />
      ))}
      {supervisorBrief && <AgentCard agentName="SupervisorAgent" output={supervisorBrief} index={agentEntries.length} />}
    </div>
  )
}

function AgentCard({ agentName, output, index }) {
  const [expanded, setExpanded] = useState(index === 0)
  return (
    <div className="bg-slate-800/40 rounded-xl border border-slate-700/50 overflow-hidden">
      <button onClick={() => setExpanded(!expanded)} className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-700/20">
        <div className="flex items-center gap-3">
          <div className="text-left">
            <p className="text-sm font-semibold text-slate-200">{agentName.replace(/([A-Z])/g, ' $1').trim()}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {output?.status === 'completed' ? <span className="text-green-400 flex items-center gap-1 text-xs"><CheckCircle2 className="w-3.5 h-3.5" /> Done</span> : <span className="text-sky-400 text-xs">...</span>}
          <motion.div animate={{ rotate: expanded ? 180 : 0 }}><ChevronDown className="w-4 h-4 text-slate-500" /></motion.div>
        </div>
      </button>
      <AnimatePresence>
        {expanded && output && (
          <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} className="border-t border-slate-700/30 p-4">
            {output.ai_narrative ? (
              <div className="mb-3 p-3 bg-purple-500/5 border border-purple-500/20 rounded-lg">
                <p className="text-[10px] font-mono text-purple-400 mb-1">AI ANALYSIS</p>
                <p className="text-xs text-slate-300">{output.ai_narrative}</p>
              </div>
            ) : null}
            <div className="bg-slate-900/60 rounded-lg p-3 border border-slate-700/50">
              <div className="flex items-center gap-2 mb-2"><Terminal className="w-3.5 h-3.5 text-sky-400" /><p className="text-[10px] font-mono text-slate-500">RAW DATA</p></div>
              <pre className="text-xs text-slate-400 font-mono overflow-x-auto whitespace-pre-wrap">{JSON.stringify(output, null, 2)}</pre>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}