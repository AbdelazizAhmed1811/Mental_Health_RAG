import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiJson, apiFetch } from '../utils/api'
import SessionList from '../components/SessionList'
import ChatMessage from '../components/ChatMessage'
import TypingIndicator from '../components/TypingIndicator'
import './Chat.css'

const LANG_NAMES = {
  en: 'English', es: 'Spanish', ar: 'Arabic', fr: 'French', de: 'German',
  zh: 'Chinese', hi: 'Hindi', bn: 'Bengali', pt: 'Portuguese', ru: 'Russian',
  ja: 'Japanese', pa: 'Punjabi', mr: 'Marathi', te: 'Telugu', tr: 'Turkish',
  ko: 'Korean', vi: 'Vietnamese', ta: 'Tamil', it: 'Italian', ur: 'Urdu',
  nl: 'Dutch', pl: 'Polish', uk: 'Ukrainian', fa: 'Persian', ro: 'Romanian',
  el: 'Greek', cs: 'Czech', sv: 'Swedish', hu: 'Hungarian', th: 'Thai',
  id: 'Indonesian', fi: 'Finnish', da: 'Danish', he: 'Hebrew', no: 'Norwegian',
  sk: 'Slovak', hr: 'Croatian', ms: 'Malay', bg: 'Bulgarian', sr: 'Serbian'
}

export default function Chat() {
  const { user, logout } = useAuth()
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [detectedLang, setDetectedLang] = useState(null)
  const [detectedEmotion, setDetectedEmotion] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const chatBoxRef = useRef(null)
  const inputRef = useRef(null)

  // Generate session ID
  function newSessionId() {
    return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2)
  }

  // Load sessions on mount
  useEffect(() => {
    loadSessions()
  }, [])

  // Start with a new session if none exists
  useEffect(() => {
    if (!activeSessionId) {
      setActiveSessionId(newSessionId())
    }
  }, [])

  // Scroll to bottom on new messages
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTo({ top: chatBoxRef.current.scrollHeight, behavior: 'smooth' })
    }
  }, [messages, isLoading])

  async function loadSessions() {
    try {
      const data = await apiJson('/api/sessions')
      setSessions(data)
    } catch {
      // Sessions might fail if backend is down, not critical
    }
  }

  async function loadSessionMessages(sessionId) {
    try {
      const data = await apiJson(`/api/sessions/${sessionId}`)
      const msgs = []
      data.forEach((turn) => {
        msgs.push({ text: turn.user_message, sender: 'user', time: new Date(turn.timestamp) })
        msgs.push({ text: turn.bot_message, sender: 'bot', time: new Date(turn.timestamp) })
      })
      setMessages(msgs)
      setActiveSessionId(sessionId)
    } catch (err) {
      console.error('Failed to load session:', err)
    }
  }

  function handleNewSession() {
    const id = newSessionId()
    setActiveSessionId(id)
    setMessages([])
    setDetectedLang(null)
    setDetectedEmotion(null)
    inputRef.current?.focus()
  }

  async function handleDeleteSession(sessionId) {
    try {
      await apiFetch(`/api/sessions/${sessionId}`, { method: 'DELETE' })
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId))
      if (activeSessionId === sessionId) {
        handleNewSession()
      }
    } catch (err) {
      console.error('Failed to delete session:', err)
    }
  }

  async function handleSend(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || isLoading) return

    // Add user message
    setMessages((prev) => [...prev, { text, sender: 'user', time: new Date() }])
    setInput('')
    setIsLoading(true)

    try {
      const res = await apiFetch('/chat', {
        method: 'POST',
        body: JSON.stringify({ query: text, session_id: activeSessionId })
      })

      if (!res.ok) throw new Error('Chat request failed')

      const data = await res.json()

      setMessages((prev) => [
        ...prev,
        {
          text: data.response,
          sender: 'bot',
          time: new Date(),
          meta: {
            lang: data.detected_language,
            intent: data.detected_intent,
            emotion: data.detected_emotion
          }
        }
      ])

      if (data.detected_language) setDetectedLang(data.detected_language)
      if (data.detected_emotion) setDetectedEmotion(data.detected_emotion)

      // Refresh session list
      loadSessions()
    } catch (err) {
      console.error(err)
      setMessages((prev) => [
        ...prev,
        { text: '⚠️ Something went wrong. Please try again.', sender: 'bot', time: new Date() }
      ])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const formatTime = (date) => {
    if (!(date instanceof Date) || isNaN(date)) return ''
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const handleInputResize = (e) => {
    setInput(e.target.value)
    // Auto-resize magic
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
  }

  return (
    <div className="chat-app">
      {/* ─── Sidebar ────────────────────────── */}
      <aside className={`chat-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <Link to="/" className="sidebar-brand" style={{ textDecoration: 'none' }}>
            <span className="brand-icon">🌿</span>
            <span>Companion</span>
          </Link>
          <button className="sidebar-close-btn" onClick={() => setSidebarOpen(false)}>
            ✕
          </button>
        </div>

        <button className="new-chat-btn" onClick={handleNewSession}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 4v16m8-8H4"/></svg>
          New Chat
        </button>

        <SessionList
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelect={loadSessionMessages}
          onDelete={handleDeleteSession}
        />

        {/* User section */}
        <div className="sidebar-user">
          <img
            src={user?.avatar_url || ''}
            alt=""
            className="sidebar-user-avatar"
            referrerPolicy="no-referrer"
          />
          <div className="sidebar-user-info">
            <span className="sidebar-user-name">{user?.display_name || 'User'}</span>
            <span className="sidebar-user-email">{user?.email || ''}</span>
          </div>
          <button className="sidebar-logout-btn" onClick={logout} title="Sign out">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/></svg>
          </button>
        </div>
      </aside>

      {/* ─── Main Chat ──────────────────────── */}
      <main className="chat-main">
        {/* Header */}
        <header className="chat-header">
          <div className="chat-header-left">
            <button className="hamburger-btn" onClick={() => setSidebarOpen(true)}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
            </button>
            <div>
              <h1>Your Companion</h1>
              <span className={`status ${isLoading ? 'loading' : ''}`}>
                <span className="status-dot" />
                {isLoading ? 'Typing…' : 'Online'}
              </span>
            </div>
          </div>
          <div className="chat-header-right">
            {detectedEmotion && (
              <span className={`emotion-pill ${detectedEmotion}`}>
                {detectedEmotion.charAt(0).toUpperCase() + detectedEmotion.slice(1)}
              </span>
            )}
            {detectedLang && (
              <span className="lang-pill">
                🌐 {LANG_NAMES[detectedLang] || detectedLang.toUpperCase()}
              </span>
            )}
          </div>
        </header>

        {/* Centered Wrapper */}
        <div className="chat-container">
          {/* Messages */}
          <div className="chat-messages" ref={chatBoxRef}>
            {messages.length === 0 && (
              <div className="welcome-msg">
                <div className="welcome-icon">🌿</div>
                <h2>Welcome{user?.display_name ? `, ${user.display_name.split(' ')[0]}` : ''}!</h2>
                <p>I'm your safe space — here to listen and support your mental well-being. Feel free to share how you're feeling. I understand <strong>20+ languages</strong>, so speak naturally.</p>
              </div>
            )}

            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} formatTime={formatTime} />
            ))}

            {isLoading && <TypingIndicator />}
          </div>

          {/* Input */}
          <div className="chat-input-area">
            <form className="chat-input-form" onSubmit={handleSend}>
              <textarea
                ref={inputRef}
                value={input}
                onChange={handleInputResize}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend(e)
                  }
                }}
                placeholder="Share how you're feeling... (any language)"
                rows={1}
                style={{ height: 'auto' }}
                disabled={isLoading}
              />
              <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
                <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" strokeWidth="2" fill="none">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </form>
            <div className="chat-input-meta">
              <span className="char-count">{input.length > 0 ? `${input.length}` : ''}</span>
              <span className="disclaimer">Private & secure session · For severe crises, please contact emergency services.</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
