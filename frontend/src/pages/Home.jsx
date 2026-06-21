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
        
        {/* Floating Background Shapes */}
        <div className="floating-shape shape-1"><svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg></div>
        <div className="floating-shape shape-2"><svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><circle cx="12" cy="12" r="10"/></svg></div>
        <div className="floating-shape shape-3"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg></div>

        <div className="container hero-content" style={{ textAlign: 'center' }}>
          <div className="hero-badge">🧠 AI-Powered Mental Health Support</div>
          <h1 className="hero-title">
            Your Safe Space for<br />
            <span className="gradient-text">Mental Wellness</span>
          </h1>
          <p className="hero-subtitle" style={{ marginLeft: 'auto', marginRight: 'auto' }}>
            Share how you're feeling in any language. Our AI companion listens with empathy,
            detects your emotions, and offers evidence-based support — completely private and judgment-free.
          </p>
          <div className="hero-actions" style={{ justifyContent: 'center' }}>
            <Link to="/login" className="btn btn-primary btn-lg">
              Start Chatting Free
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </Link>
            <a href="#features" className="btn btn-outline btn-lg">Learn More</a>
          </div>
          <div className="hero-stats" style={{ justifyContent: 'center' }}>
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
            <p>Built with cutting-edge AI technology to understand and support you.</p>
          </div>
          <div className="features-grid">
            {[
              {
                icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>,
                title: 'Multilingual Support',
                desc: 'Speak in your native language — Arabic, Spanish, German, and 20+ more. Our AI auto-detects and responds naturally.'
              },
              {
                icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 18h1.4c1.3 0 2.5-.6 3.3-1.7l6.1-8.6c.7-1.1 2-1.7 3.3-1.7H22"/><path d="m18 2 4 4-4 4"/><path d="M2 6h1.9c1.5 0 2.9.9 3.6 2.2"/><path d="M22 18h-2.4c-1.3 0-2.5-.6-3.3-1.7l-1.2-1.6"/></svg>,
                title: 'Evidence-Based RAG',
                desc: 'Powered by Retrieval-Augmented Generation from real counselor conversations, ensuring grounded and empathetic responses.'
              },
              {
                icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.78-.77-.78a5.4 5.4 0 0 0-7.65 0C1.46 6.7 1.33 10.28 4 13l8 8 8-8c2.67-2.72 2.54-6.3.42-8.42z"/></svg>,
                title: 'Emotion-Aware',
                desc: 'Detects your emotional state (joy, sadness, anxiety, anger, fear, surprise) and adapts its tone to match what you need.'
              },
              {
                icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>,
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
      <section className="how-it-works" id="how-it-works">
        <div className="container">
          <div className="section-header" ref={addRevealRef}>
            <h2>How Our AI Works</h2>
            <p>A sophisticated 4-step natural language processing pipeline to give you the best support.</p>
          </div>
          <div className="steps-pipeline">
            {[
              { 
                num: '01', 
                icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/></svg>, 
                title: 'Language Translation', 
                desc: 'You type in any language. The AI detects it and translates it to English internally for high-accuracy processing.' 
              },
              { 
                num: '02', 
                icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="m12 16 4-4-4-4"/><path d="M8 12h8"/></svg>, 
                title: 'Intent Classification', 
                desc: 'We classify your intent. If you just want to say "Hello", we reply instantly. If you need support, we route you to the RAG engine.' 
              },
              { 
                num: '03', 
                icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z"/><path d="M12 14c-1.5 0-3-.5-4-1.5"/><path d="M9 9h.01"/><path d="M15 9h.01"/></svg>, 
                title: 'Emotion Detection', 
                desc: 'An NLP model analyzes your message to detect underlying emotions like sadness, anxiety, or joy to tailor our tone.' 
              },
              { 
                num: '04', 
                icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>, 
                title: 'Empathetic RAG', 
                desc: 'We search a database of real counseling transcripts and use them to generate a safe, empathetic response, translated back to you.' 
              }
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
        <div className="cta-bg-glow" />
        <div className="container">
          <div className="cta-content glass-card">
            <h2>Ready to Start Your Journey?</h2>
            <p>Join Companion today — a safe, private space to express yourself in over 20+ languages.</p>
            <Link to="/login" className="btn btn-primary btn-lg cta-btn">
              Get Started for Free
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </Link>
          </div>
        </div>
      </section>

      {/* ─── Footer ─────────────────────────── */}
      <footer className="home-footer">
        <div className="container">
          <div className="footer-grid">
            <div className="footer-brand-col">
              <div className="footer-brand">
                <span className="brand-icon">🌿</span>
                <span>Companion</span>
              </div>
              <p className="footer-disclaimer">
                Companion is an AI emotional support assistant, <strong>not a licensed therapist</strong>.
                If you are in a crisis, please contact emergency services immediately.
              </p>
            </div>
            
            <div className="footer-links-col">
              <h4>Platform</h4>
              <a href="#features">Features</a>
              <a href="#how-it-works">How it Works</a>
              <a href="#security">Security & Privacy</a>
            </div>
            
            <div className="footer-links-col">
              <h4>Legal</h4>
              <a href="#">Terms of Service</a>
              <a href="#">Privacy Policy</a>
              <a href="#">Cookie Policy</a>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p className="footer-copy">© {new Date().getFullYear()} Companion Mental Health AI. All rights reserved.</p>
            <div className="footer-social">
              <a href="#" aria-label="Twitter">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
              </a>
              <a href="#" aria-label="GitHub">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
