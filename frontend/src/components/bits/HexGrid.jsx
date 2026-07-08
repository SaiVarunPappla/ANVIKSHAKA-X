import React from 'react'

export default function HexGrid() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.03]">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="hexPattern" width="56" height="100" patternUnits="userSpaceOnUse">
            <polygon points="28,0 56,16 56,48 28,64 0,48 0,16" fill="none" stroke="#38bdf8" strokeWidth="1" />
            <polygon points="28,64 56,80 56,112 28,128 0,112 0,80" fill="none" stroke="#38bdf8" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#hexPattern)" />
      </svg>
    </div>
  )
}
