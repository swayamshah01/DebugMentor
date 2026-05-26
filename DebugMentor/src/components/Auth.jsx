import { useState } from 'react'
import axios from 'axios'
import { useTheme } from '../context/ThemeContext'

const API_BASE = 'http://localhost:8000/api'

export default function Auth({ setToken, setUsername, onBackToLanding }) {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({ email: '', password: '' })
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const { theme, toggleTheme } = useTheme()

  const parseUsernameFromToken = (token) => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.username || null
    } catch {
      return null
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      let access_token
      const email = formData.email.trim().toLowerCase()

      if (isLogin) {
        const formParams = new URLSearchParams()
        formParams.append('username', email)
        formParams.append('password', formData.password)
        const response = await axios.post(`${API_BASE}/login`, formParams, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        access_token = response.data.access_token
      } else {
        const response = await axios.post(`${API_BASE}/register`, {
          email,
          password: formData.password,
        })
        access_token = response.data.access_token
      }

      localStorage.setItem('token', access_token)
      const name = parseUsernameFromToken(access_token)
      if (name) {
        localStorage.setItem('username', name)
        setUsername(name)
      }
      setToken(access_token)
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${isLogin ? 'sign in' : 'register'}. Is the backend running?`)
    } finally {
      setIsLoading(false)
    }
  }

  const inputStyle = {
    width: '100%',
    padding: '11px 14px',
    background: 'var(--bg-surface)',
    border: '1px solid var(--border-bright)',
    borderRadius: 8,
    color: 'var(--text-primary)',
    outline: 'none',
    fontFamily: 'var(--font-body)',
    fontSize: 14,
    transition: 'border-color 0.2s',
    boxSizing: 'border-box',
  }

  const labelStyle = {
    display: 'block',
    fontSize: 11,
    fontWeight: 700,
    color: 'var(--text-secondary)',
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: '0.07em',
  }

  const updateField = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }))
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-base)',
      color: 'var(--text-primary)',
      fontFamily: 'var(--font-body)',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <nav style={{
        height: 60,
        display: 'flex',
        alignItems: 'center',
        padding: '0 28px',
        borderBottom: '1px solid var(--border)',
        flexShrink: 0,
      }}>
        <button
          id="auth-back-btn"
          onClick={onBackToLanding}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            fontFamily: 'var(--font-body)',
            fontSize: 13,
            cursor: 'pointer',
          }}
        >
          Back
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '0 auto' }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-bright)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'var(--font-mono)',
            fontSize: 13,
            fontWeight: 'bold',
            color: 'var(--accent-primary)',
          }}>DM</div>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 16, fontWeight: 700 }}>
            Debug<span style={{ color: 'var(--accent-primary)' }}>Mentor</span>
          </span>
        </div>

        <button
          onClick={toggleTheme}
          style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-bright)',
            borderRadius: 8,
            color: 'var(--text-primary)',
            cursor: 'pointer',
            fontSize: 13,
            padding: '7px 12px',
          }}
        >
          {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
      </nav>

      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '32px 20px',
      }}>
        <div style={{ width: '100%', maxWidth: 420 }} className="fade-in">
          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-bright)',
            borderRadius: 12,
            padding: '34px 32px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.18)',
          }}>
            <div style={{ marginBottom: 28 }}>
              <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 6 }}>
                {isLogin ? 'Sign in' : 'Create account'}
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
                {isLogin
                  ? 'Use your email and password to open your workspace.'
                  : 'Create one account with your email. Your display name is generated automatically.'}
              </p>
            </div>

            {error && (
              <div className="fade-in" style={{
                background: 'rgba(220,38,38,0.08)',
                border: '1px solid rgba(220,38,38,0.3)',
                borderRadius: 8,
                padding: '10px 14px',
                marginBottom: 20,
                color: 'var(--accent-danger)',
                fontSize: 13,
                lineHeight: 1.5,
              }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
              <div>
                <label style={labelStyle}>Email</label>
                <input
                  id="auth-email"
                  required
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  style={inputStyle}
                  onFocus={(e) => { e.target.style.borderColor = 'var(--accent-primary)' }}
                  onBlur={(e) => { e.target.style.borderColor = 'var(--border-bright)' }}
                />
              </div>

              <div>
                <label style={labelStyle}>Password</label>
                <input
                  id="auth-password"
                  required
                  type="password"
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  placeholder={isLogin ? 'Your password' : 'Min 8 characters'}
                  value={formData.password}
                  onChange={(e) => updateField('password', e.target.value)}
                  style={inputStyle}
                  onFocus={(e) => { e.target.style.borderColor = 'var(--accent-primary)' }}
                  onBlur={(e) => { e.target.style.borderColor = 'var(--border-bright)' }}
                />
              </div>

              <button
                id="auth-submit-btn"
                type="submit"
                disabled={isLoading}
                style={{
                  marginTop: 4,
                  padding: '13px 16px',
                  background: 'var(--accent-primary)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 8,
                  fontWeight: 700,
                  fontSize: 15,
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  opacity: isLoading ? 0.75 : 1,
                }}
              >
                {isLoading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
              </button>
            </form>

            <p style={{ marginTop: 24, textAlign: 'center', fontSize: 13, color: 'var(--text-secondary)' }}>
              {isLogin ? 'New to DebugMentor?' : 'Already have an account?'}
              {' '}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin)
                  setError(null)
                  setFormData({ email: '', password: '' })
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--accent-primary)',
                  fontWeight: 600,
                  fontSize: 13,
                  cursor: 'pointer',
                }}
              >
                {isLogin ? 'Register free' : 'Sign in instead'}
              </button>
            </p>
          </div>

          <p style={{
            marginTop: 20,
            textAlign: 'center',
            fontSize: 12,
            color: 'var(--text-secondary)',
            opacity: 0.75,
          }}>
            Your practice history stays connected to your email account.
          </p>
        </div>
      </div>
    </div>
  )
}
