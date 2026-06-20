import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import { useAuth } from '../context/AuthContext'
import './Login.css'

export default function Login() {
  const { loginWithGoogle, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat', { replace: true })
    }
  }, [isAuthenticated, navigate])

  async function handleGoogleSuccess(credentialResponse) {
    setError('')
    setLoading(true)
    try {
      await loginWithGoogle(credentialResponse.credential)
      navigate('/chat', { replace: true })
    } catch (err) {
      setError('Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  function handleGoogleError() {
    setError('Google sign-in was cancelled or failed.')
  }

  return (
    <div className="login-page">
      {/* Decorative left panel */}
      <div className="login-decor">
        <div className="login-decor-content">
          <Link to="/" className="login-brand">
            <span className="brand-icon">🌿</span>
            <span className="brand-name">Companion</span>
          </Link>
          <h2>Welcome to your<br />safe space</h2>
          <p>A judgment-free AI companion that listens, understands, and supports your mental well-being.</p>
          <div className="login-decor-features">
            <div className="login-feature">
              <span>🌍</span> 20+ Languages
            </div>
            <div className="login-feature">
              <span>🧠</span> Evidence-Based
            </div>
            <div className="login-feature">
              <span>🔒</span> Fully Private
            </div>
          </div>
        </div>
      </div>

      {/* Login form panel */}
      <div className="login-form-panel">
        <div className="login-card glass-card">
          <div className="login-card-header">
            <h1>Sign In</h1>
            <p>Continue with your Google account to get started.</p>
          </div>

          {error && (
            <div className="login-error">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
              {error}
            </div>
          )}

          <div className="google-btn-wrapper">
            {loading ? (
              <div className="login-loading">Signing you in...</div>
            ) : (
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                size="large"
                width="320"
                text="signin_with"
                shape="pill"
                theme="outline"
              />
            )}
          </div>

          <div className="login-divider">
            <span>secure sign-in via Google</span>
          </div>

          <p className="login-footer-text">
            By signing in, you agree to use this tool responsibly.
            <br />
            <Link to="/">← Back to home</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
