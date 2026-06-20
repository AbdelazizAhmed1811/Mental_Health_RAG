import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      fetchUser(token)
    } else {
      setLoading(false)
    }
  }, [])

  async function fetchUser(jwt) {
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${jwt}` }
      })
      if (res.ok) {
        const data = await res.json()
        setUser(data)
        setToken(jwt)
      } else {
        // Token expired or invalid
        localStorage.removeItem('token')
        setToken(null)
        setUser(null)
      }
    } catch {
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  async function loginWithGoogle(googleToken) {
    const res = await fetch('/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: googleToken })
    })

    if (!res.ok) {
      throw new Error('Login failed')
    }

    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
    return data
  }

  function logout() {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      isAuthenticated: !!user,
      loginWithGoogle,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
