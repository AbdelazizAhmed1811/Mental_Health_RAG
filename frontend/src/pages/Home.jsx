import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Home.css'

export default function Home() {
  const { isAuthenticated } = useAuth()
  const revealRefs = useRef([])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible')
          }
        })
      },
      { threshold: 0.15 }
    )

    revealRefs.current.forEach((el) => {
      if (el) observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  const addRevealRef = (el) => {
    if (el && !revealRefs.current.includes(el)) {
      revealRefs.current.push(el)
    }
  }

  return (
    <div className="home">
      {/* ─── Navbar ─────────────────────────── */}
      <nav className="home-nav">
        <div className="container home-nav-inner">
          <div className="home-nav-brand">
            <span className="brand-icon">🌿</span>
            <span className="brand-name">Companion</span>
          </div>
          <div className="home-nav-links">
            {isAuthenticated ? (
              <Link to="/chat" className="btn btn-primary btn-sm">Open Chat</Link>
            ) : (
              <>
                <Link to="/login" className="nav-link">Sign In</Link>
                <Link to="/login" className="btn btn-primary btn-sm">Get Started</Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* ─── Hero ───────────────────────────── */}
      <section className="hero">
        <div className="hero-bg-glow" />
        <div className="container hero-content">
          <div className="hero-badge">🧠 AI-Powered Mental Health Support</div>
          <h1 className="hero-title">
            Your Safe Space for<br />
            <span className="gradient-text">Mental Wellness</span>
          </h1>
          <p className="hero-subtitle">
            Share how you're feeling in any language. Our AI companion listens with empathy,
            detects your emotions, and offers evidence-based support — completely private and judgment-free.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="btn btn-primary btn-lg">
              Start Chatting Free
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </Link>
            <a href="#features" className="btn btn-outline btn-lg">Learn More</a>
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <strong>20+</strong>
              <span>Languages</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <strong>6</strong>
              <span>Emotions Detected</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <strong>100%</strong>
              <span>Private</span>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Features ───────────────────────── */}
      <section className="features" id="features">
        <div className="container">
          <div className="section-header" ref={addRevealRef}>
            <h2>Why Companion?</h2>
            <p>Built with cutting-edge NLP technology to understand and support you.</p>
          </div>
          <div className="features-grid">
            {[
              {
                icon: '🌍',
                title: 'Multilingual Support',
                desc: 'Speak in your native language — Arabic, Spanish, German, and 20+ more. Our AI auto-detects and responds naturally.'
              },
              {
                icon: '🧠',
                title: 'Evidence-Based RAG',
                desc: 'Powered by Retrieval-Augmented Generation from real counselor conversations, ensuring grounded and empathetic responses.'
              },
              {
                icon: '💬',
                title: 'Emotion-Aware',
                desc: 'Detects your emotional state (joy, sadness, anxiety, anger, fear, surprise) and adapts its tone to match what you need.'
              },
              {
                icon: '🔒',
                title: 'Private & Secure',
                desc: 'Your conversations stay yours. Sign in with Google for a personalized experience with full session history.'
              }
            ].map((feat, i) => (
              <div className="feature-card glass-card" key={i} ref={addRevealRef} style={{ transitionDelay: `${i * 0.1}s` }}>
                <div className="feature-card-icon">{feat.icon}</div>
                <h3>{feat.title}</h3>
                <p>{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How It Works ───────────────────── */}
      <section className="how-it-works">
        <div className="container">
          <div className="section-header" ref={addRevealRef}>
            <h2>How It Works</h2>
            <p>Three simple steps to start feeling supported.</p>
          </div>
          <div className="steps">
            {[
              { num: '01', icon: '✍️', title: 'Share Your Feelings', desc: 'Type anything in any language. Our AI understands context, emotion, and nuance.' },
              { num: '02', icon: '⚡', title: 'AI Analyzes & Retrieves', desc: 'Your message is analyzed for intent, emotion, and matched with evidence-based counselor responses.' },
              { num: '03', icon: '💚', title: 'Get Empathetic Support', desc: 'Receive a thoughtful, personalized response tailored to your emotional state and language.' }
            ].map((step, i) => (
              <div className="step-card" key={i} ref={addRevealRef} style={{ transitionDelay: `${i * 0.15}s` }}>
                <div className="step-num">{step.num}</div>
                <div className="step-icon">{step.icon}</div>
                <h3>{step.title}</h3>
                <p>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA ────────────────────────────── */}
      <section className="cta" ref={addRevealRef}>
        <div className="container cta-content">
          <h2>Ready to Start Your Journey?</h2>
          <p>Join Companion today — it's free, private, and available in 20+ languages.</p>
          <Link to="/login" className="btn btn-primary btn-lg">
            Get Started Now
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </Link>
        </div>
      </section>

      {/* ─── Footer ─────────────────────────── */}
      <footer className="home-footer">
        <div className="container footer-content">
          <div className="footer-brand">
            <span className="brand-icon">🌿</span>
            <span>Companion</span>
          </div>
          <p className="footer-disclaimer">
            Companion is an AI assistant, <strong>not a licensed therapist</strong>.
            In a crisis, please call <strong>emergency services</strong> or a local helpline.
          </p>
          <p className="footer-copy">© 2026 Companion · Mental Health AI</p>
        </div>
      </footer>
    </div>
  )
}
