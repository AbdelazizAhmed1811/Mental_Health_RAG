import React from 'react'

export default function ChatMessage({ message, formatTime }) {
  const isBot = message.sender === 'bot'
  
  return (
    <div className={`message ${isBot ? 'bot-message' : 'user-message'}`}>
      {isBot ? (
        <div className="avatar bot-avatar">🌿</div>
      ) : (
        <div className="avatar user-avatar">You</div>
      )}
      
      <div className="message-content">
        <p>{message.text}</p>
        
        <div className="message-meta">
          <span className="timestamp">{formatTime(message.time)}</span>
          
          {isBot && message.meta && message.meta.intent !== 'out_of_scope' && (
            <span className="meta-pill">✓ RAG Verified</span>
          )}
        </div>
      </div>
    </div>
  )
}
