import { Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import TacticalBackground from './components/TacticalBackground'
import Dashboard from './pages/Dashboard'
import MissionPlanner from './pages/MissionPlanner'
import RiskDashboard from './pages/RiskDashboard'
import Maintenance from './pages/Maintenance'
import Analytics from './pages/Analytics'
import Chat from './pages/Chat'

// Page transition variants
const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 }
}

const pageTransition = {
  duration: 0.25,
  ease: 'easeOut'
}

function App() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-navy-900 text-slate-100 flex overflow-hidden">
      <TacticalBackground />
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64 relative z-10">
        <Navbar />
        <main className="flex-1 p-6 overflow-y-auto custom-scrollbar">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial="initial"
              animate="animate"
              exit="exit"
              variants={pageVariants}
              transition={pageTransition}
            >
              <Routes location={location}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/mission-planner" element={<MissionPlanner />} />
                <Route path="/risk" element={<RiskDashboard />} />
                <Route path="/maintenance" element={<Maintenance />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/chat" element={<Chat />} />
              </Routes>
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}

export default App