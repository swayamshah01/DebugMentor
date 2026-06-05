import { useMemo, useState } from 'react'
import axios from 'axios'
import { useTheme } from '../context/ThemeContext'

const API_BASE = 'http://localhost:8000/api'

function validatePassword(password) {
  return {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    digit: /\d/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  }
}

function formatApiError(error, fallbackMessage) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => item?.msg || item?.message || null)
      .filter(Boolean)
      .join(' ')
  }
  return fallbackMessage
}

export default function Auth({ setToken, setUsername, onBackToLanding }) {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    loginId: '',
    username: '',
    email: '',
    password: '',
  })
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const { theme, toggleTheme } = useTheme()

  const passwordChecks = useMemo(() => validatePassword(formData.password), [formData.password])
  const passwordStrong = Object.values(passwordChecks).every(Boolean)

  const parseUsernameFromToken = (token) => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.username || null
    } catch {
      return null
    }
  }

  const updateField = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }))
  }

  const switchMode = () => {
    setIsLogin((current) => !current)
    setError(null)
    setFormData({
      loginId: '',
      username: '',
      email: '',
      password: '',
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!isLogin && !passwordStrong) {
      setError('Password does not meet the required strength rules.')
      return
    }

    setIsLoading(true)

    try {
      let accessToken

      if (isLogin) {
        const formParams = new URLSearchParams()
        formParams.append('username', formData.loginId.trim())
        formParams.append('password', formData.password)

        const response = await axios.post(`${API_BASE}/login`, formParams, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        accessToken = response.data.access_token
      } else {
        const response = await axios.post(`${API_BASE}/register`, {
          username: formData.username.trim(),
          email: formData.email.trim().toLowerCase(),
          password: formData.password,
        })
        accessToken = response.data.access_token
      }

      localStorage.setItem('token', accessToken)
      const name = parseUsernameFromToken(accessToken)
      if (name) {
        localStorage.setItem('username', name)
        setUsername(name)
      }
      setToken(accessToken)
    } catch (err) {
      setError(formatApiError(err, `Failed to ${isLogin ? 'sign in' : 'register'}. Is the backend running?`))
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

  const checklistItem = (_, ok) => ({
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    fontSize: 12,
    color: ok ? 'var(--accent-primary)' : 'var(--text-secondary)',
  })

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
        <div style={{ width: '100%', maxWidth: 460 }} className="fade-in">
          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-bright)',
            borderRadius: 14,
            padding: '34px 32px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.18)',
          }}>
            <div style={{ marginBottom: 28 }}>
              <div style={{ display: 'inline-flex', gap: 8, padding: 4, borderRadius: 999, background: 'var(--bg-surface)', border: '1px solid var(--border)', marginBottom: 18 }}>
                <button
                  type="button"
                  onClick={() => setIsLogin(true)}
                  style={{
                    border: 'none',
                    borderRadius: 999,
                    padding: '8px 14px',
                    background: isLogin ? 'var(--accent-primary)' : 'transparent',
                    color: isLogin ? '#fff' : 'var(--text-secondary)',
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  Login
                </button>
                <button
                  type="button"
                  onClick={() => setIsLogin(false)}
                  style={{
                    border: 'none',
                    borderRadius: 999,
                    padding: '8px 14px',
                    background: !isLogin ? 'var(--accent-primary)' : 'transparent',
                    color: !isLogin ? '#fff' : 'var(--text-secondary)',
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  Sign up
                </button>
              </div>

              <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 6 }}>
                {isLogin ? 'Welcome back' : 'Create your DebugMentor account'}
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.6 }}>
                {isLogin
                  ? 'Use your username or email with your password to continue your practice.'
                  : 'Choose a unique username and a strong password so your progress, streaks, and badges stay attached to one account.'}
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
              {isLogin ? (
                <div>
                  <label style={labelStyle}>Username or Email</label>
                  <input
                    id="auth-login-id"
                    required
                    type="text"
                    autoComplete="username"
                    placeholder="username or you@example.com"
                    value={formData.loginId}
                    onChange={(e) => updateField('loginId', e.target.value)}
                    style={inputStyle}
                  />
                </div>
              ) : (
                <>
                  <div>
                    <label style={labelStyle}>Username</label>
                    <input
                      id="auth-username"
                      required
                      type="text"
                      autoComplete="username"
                      placeholder="letters, numbers, underscores"
                      value={formData.username}
                      onChange={(e) => updateField('username', e.target.value)}
                      style={inputStyle}
                    />
                  </div>

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
                    />
                  </div>
                </>
              )}

              <div>
                <label style={labelStyle}>Password</label>
                <input
                  id="auth-password"
                  required
                  type="password"
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  placeholder={isLogin ? 'Your password' : 'Choose a strong password'}
                  value={formData.password}
                  onChange={(e) => updateField('password', e.target.value)}
                  style={inputStyle}
                />
              </div>

              {!isLogin && (
                <div style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border)',
                  borderRadius: 10,
                  padding: 14,
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 10,
                }}>
                  <div style={checklistItem('At least 8 characters', passwordChecks.length)}>
                    <span>{passwordChecks.length ? 'OK' : '-'}</span>
                    <span>8+ characters</span>
                  </div>
                  <div style={checklistItem('One uppercase letter', passwordChecks.upper)}>
                    <span>{passwordChecks.upper ? 'OK' : '-'}</span>
                    <span>1 uppercase</span>
                  </div>
                  <div style={checklistItem('One lowercase letter', passwordChecks.lower)}>
                    <span>{passwordChecks.lower ? 'OK' : '-'}</span>
                    <span>1 lowercase</span>
                  </div>
                  <div style={checklistItem('One digit', passwordChecks.digit)}>
                    <span>{passwordChecks.digit ? 'OK' : '-'}</span>
                    <span>1 digit</span>
                  </div>
                  <div style={checklistItem('One special character', passwordChecks.special)}>
                    <span>{passwordChecks.special ? 'OK' : '-'}</span>
                    <span>1 special</span>
                  </div>
                </div>
              )}

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
                  borderRadius: 10,
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
              {isLogin ? 'Need a new account?' : 'Already have an account?'}
              {' '}
              <button
                type="button"
                onClick={switchMode}
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
            lineHeight: 1.6,
          }}>
            Your profile stores submissions, streaks, badges, and learning progress under the same account.
          </p>
        </div>
      </div>
    </div>
  )
}
