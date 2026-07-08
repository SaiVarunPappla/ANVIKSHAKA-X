import React from 'react'

export default function RadarScan({ size = 48 }) {
  return (
    <div style={{ width: size, height: size }} className="relative">
      <svg width={size} height={size} viewBox="0 0 100 100" className="overflow-visible">
        <circle cx="50" cy="50" r="48" fill="none" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="1" />
        <circle cx="50" cy="50" r="32" fill="none" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="1" />
        <circle cx="50" cy="50" r="16" fill="none" stroke="rgba(56, 189, 248, 0.2)" strokeWidth="1" />
        <line x1="50" y1="2" x2="50" y2="98" stroke="rgba(56, 189, 248, 0.15)" strokeWidth="0.5" />
        <line x1="2" y1="50" x2="98" y2="50" stroke="rgba(56, 189, 248, 0.15)" strokeWidth="0.5" />
        <g style={{ transformOrigin: '50% 50%', animation: 'spin 3s linear infinite' }}>
          <path d="M 50 50 L 50 2 A 48 48 0 0 1 95 35 Z" fill="rgba(56, 189, 248, 0.4)" />
          <line x1="50" y1="50" x2="50" y2="2" stroke="#38bdf8" strokeWidth="1.5" />
        </g>
      </svg>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}