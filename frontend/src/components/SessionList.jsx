import React from 'react'

export default function SessionList({ sessions, activeSessionId, onSelect, onDelete }) {
  if (!sessions || sessions.length === 0) {
    return (
      <div className="session-list-empty">
        <p>No past sessions yet.</p>
      </div>
    )
  }

  // Group sessions by date (e.g., "Today", "Yesterday", "Previous 7 Days")
  // For simplicity, just listing them chronologically (newest first)
  return (
    <div className="session-list">
      <div className="session-list-title">Recent Conversations</div>
      {sessions.map((session) => {
        const isActive = session.session_id === activeSessionId
        const date = new Date(session.timestamp)
        const timeStr = isNaN(date) ? '' : date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
        
        // Use a generic dot if no emotion, or the specific one
        const emotionClass = session.emotion ? `emotion-dot ${session.emotion.toLowerCase()}` : 'emotion-dot neutral'

        return (
          <div
            key={session.session_id}
            className={`session-item ${isActive ? 'active' : ''}`}
            onClick={() => onSelect(session.session_id)}
          >
            <div className={emotionClass} />
            <div className="session-info">
              <div className="session-preview">
                {session.preview || 'New conversation'}
              </div>
              <div className="session-time">{timeStr}</div>
            </div>
            
            <button
              className="delete-session-btn"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(session.session_id)
              }}
              title="Delete session"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
              </svg>
            </button>
          </div>
        )
      })}
    </div>
  )
}
