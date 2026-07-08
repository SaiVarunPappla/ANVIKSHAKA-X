import React, { useState, useEffect } from 'react'

export default function TypewriterText({ text, speed = 40, className = '', onComplete, startDelay = 0 }) {
  const [displayText, setDisplayText] = useState('')
  const [showCursor, setShowCursor] = useState(true)

  useEffect(() => {
    setDisplayText('')
    let i = 0
    let interval

    const timeout = setTimeout(() => {
      interval = setInterval(() => {
        if (i < text.length) {
          setDisplayText(text.slice(0, i + 1))
          i++
        } else {
          clearInterval(interval)
          if (onComplete) onComplete()
          setInterval(() => setShowCursor(prev => !prev), 530)
        }
      }, speed)
    }, startDelay)

    return () => {
      clearTimeout(timeout)
      clearInterval(interval)
    }
  }, [text, speed, startDelay, onComplete])

  return (
    <span className={className}>
      {displayText}
      {showCursor && <span className="inline-block w-[2px] h-[1em] bg-sky-400 ml-1 align-middle animate-pulse" />}
    </span>
  )
}
