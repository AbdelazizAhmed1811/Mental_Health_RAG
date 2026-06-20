import React from 'react'

export default function TypingIndicator() {
  return (
    <div className="message bot-message">
      <div className="avatar bot-avatar">🌿</div>
      <div className="typing-indicator">
        <div className="dot" />
        <div className="dot" />
        <div className="dot" />
      </div>
    </div>
  )
}
