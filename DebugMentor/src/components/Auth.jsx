import { useMemo, useState } from 'react'
import axios from 'axios'

import { useTheme } from '../context/useTheme'


const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'


function readError(error) {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(' ')
  return 'The server could not complete this request.'
}


export default function Auth({ onAuthenticated }) {
  const { theme, toggleTheme } = useTheme()
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ loginId: '', username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const passwordChecks = useMemo(() => ({
    length: form.password.length >= 8,
    upper: /[A-Z]/.test(form.password),
    lower: /[a-z]/.test(form.password),
    digit: /\d/.test(form.password),
    special: /[^A-Za-z0-9]/.test(form.password),
  }), [form.password])

  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }))

  const switchMode = (nextMode) => {
    setMode(nextMode)
    setError('')
  }

  const submit = async (event) => {
    event.preventDefault()
    setError('')

    if (mode === 'register' && !Object.values(passwordChecks).every(Boolean)) {
      setError('Password must satisfy every requirement below.')
      return
    }

    setSubmitting(true)
    try {
      let response
      if (mode === 'login') {
        const body = new URLSearchParams()
        body.set('username', form.loginId.trim())
        body.set('password', form.password)
        response = await axios.post(`${API_BASE}/login`, body, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
      } else {
        response = await axios.post(`${API_BASE}/register`, {
          username: form.username.trim(),
          email: form.email.trim(),
          password: form.password,
        })
      }
      onAuthenticated(response.data.access_token)
    } catch (requestError) {
      setError(readError(requestError))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <header className="auth-header">
        <div className="brand-mark">DM</div>
        <div className="brand-name">DebugMentor</div>
        <button className="button button-quiet auth-theme" type="button" onClick={toggleTheme}>
          {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
      </header>

      <section className="auth-panel" aria-labelledby="auth-title">
        <div className="auth-tabs" role="tablist">
          <button
            type="button"
            className={mode === 'login' ? 'active' : ''}
            onClick={() => switchMode('login')}
          >
            Sign in
          </button>
          <button
            type="button"
            className={mode === 'register' ? 'active' : ''}
            onClick={() => switchMode('register')}
          >
            Create account
          </button>
        </div>

        <div className="auth-copy">
          <h1 id="auth-title">{mode === 'login' ? 'Continue practicing' : 'Create your account'}</h1>
          <p>{mode === 'login' ? 'Your progress and submissions are waiting.' : 'Use one account for practice, hints, and progress.'}</p>
        </div>

        {error && <div className="form-error" role="alert">{error}</div>}

        <form className="auth-form" onSubmit={submit}>
          {mode === 'login' ? (
            <label>
              <span>Username or email</span>
              <input
                required
                autoComplete="username"
                value={form.loginId}
                onChange={(event) => update('loginId', event.target.value)}
              />
            </label>
          ) : (
            <>
              <label>
                <span>Username</span>
                <input
                  required
                  minLength={3}
                  autoComplete="username"
                  value={form.username}
                  onChange={(event) => update('username', event.target.value)}
                />
              </label>
              <label>
                <span>Email</span>
                <input
                  required
                  type="email"
                  autoComplete="email"
                  value={form.email}
                  onChange={(event) => update('email', event.target.value)}
                />
              </label>
            </>
          )}

          <label>
            <span>Password</span>
            <input
              required
              type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              value={form.password}
              onChange={(event) => update('password', event.target.value)}
            />
          </label>

          {mode === 'register' && (
            <div className="password-rules">
              {[
                ['length', '8+ characters'],
                ['upper', 'Uppercase'],
                ['lower', 'Lowercase'],
                ['digit', 'Number'],
                ['special', 'Special character'],
              ].map(([key, label]) => (
                <span className={passwordChecks[key] ? 'valid' : ''} key={key}>
                  <i aria-hidden="true" />{label}
                </span>
              ))}
            </div>
          )}

          <button className="button button-primary auth-submit" disabled={submitting} type="submit">
            {submitting ? 'Please wait' : (mode === 'login' ? 'Sign in' : 'Create account')}
          </button>
        </form>
      </section>
    </main>
  )
}
