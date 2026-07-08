import ParticleField from './bits/ParticleField'
import DataStream from './bits/DataStream'
import HexGrid from './bits/HexGrid'

export default function TacticalBackground() {
  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      {/* Base gradient with subtle depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-navy-950 via-navy-900 to-navy-950" />
      
      {/* Radial spotlight effect */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(56,189,248,0.03),transparent_50%)]" />
      
      {/* Layers */}
      <div className="absolute inset-0 opacity-40">
        <ParticleField />
      </div>
      <div className="absolute inset-0 opacity-30">
        <DataStream />
      </div>
      <div className="absolute inset-0 opacity-20">
        <HexGrid />
      </div>
      
      {/* Subtle vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(10,15,30,0.3)_100%)]" />
    </div>
  )
}