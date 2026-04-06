import { useState, useEffect } from 'react'
import { languageConfig } from '../data/mockData'
import { useTheme } from '../context/ThemeContext'

const LANGUAGES = ['python', 'cpp', 'java', 'javascript']

const langIconColors = {
  python: '#4B8BBE',
  cpp: '#659BD3',
  java: '#ED8B00',
  javascript: '#F7DF1E',
}

export default function Navbar({ language, onLanguageChange, backendOnline = true, username, onLogout }) {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [sessionTime, setSessionTime] = useState(0)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    const interval = setInterval(() => setSessionTime(t => t + 1), 1000)
    return () => clearInterval(interval)
  }, [])

  const formatTime = (s) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m}m ${String(sec).padStart(2, '0')}s`
  }

  // Generate initials from username
  const initials = username
    ? username.slice(0, 2).toUpperCase()
    : '??'

  // Pick a consistent color from the username (hue from char codes)
  const avatarHue = username
    ? [...username].reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360
    : 160

  const currentLang = languageConfig[language]

  return (
    <nav className="navbar">
      {/* Logo */}
      <a className="navbar-logo" href="#" onClick={e => e.preventDefault()}>
        <div className="navbar-logo-icon">&gt;_</div>
        <span className="navbar-logo-text">
          Debug<span>Mentor</span>
        </span>
      </a>

      {/* Problem badge */}
      <div className="navbar-problem-badge">
        <span className="dot" />
        <span style={{ color: 'var(--text-secondary)' }}>Problem</span>
        <span style={{ color: 'var(--text-primary)', fontWeight: 700 }}>#42</span>
        <span style={{ color: 'var(--text-secondary)' }}>—</span>
        <span style={{ color: 'var(--text-primary)' }}>Array Edge Cases</span>
      </div>

      {/* Backend status */}
      <div
        title={backendOnline ? 'Backend connected — real execution active' : 'Backend offline — using local mock'}
        style={{
          display: 'flex', alignItems: 'center', gap: 5,
          background: backendOnline ? 'rgba(79,255,176,0.08)' : 'rgba(255,95,109,0.08)',
          border: `1px solid ${backendOnline ? 'rgba(79,255,176,0.25)' : 'rgba(255,95,109,0.25)'}`,
          borderRadius: 10, padding: '3px 10px',
          fontFamily: 'var(--font-mono)', fontSize: 11,
          color: backendOnline ? 'var(--accent-primary)' : 'var(--accent-danger)',
          cursor: 'default', userSelect: 'none', transition: 'all 0.3s ease',
        }}
      >
        <span style={{
          width: 6, height: 6, borderRadius: '50%',
          background: backendOnline ? 'var(--accent-primary)' : 'var(--accent-danger)',
          display: 'inline-block',
          boxShadow: backendOnline ? '0 0 6px var(--accent-primary)' : 'none',
          animation: backendOnline ? 'pulse 2s infinite' : 'none',
        }} />
        {backendOnline ? 'API Live' : 'Offline Mode'}
      </div>

      {/* Language Selector */}
      <div className="navbar-center">
        <div className="lang-selector-wrapper">
          <button
            id="lang-selector-btn"
            className="lang-selector-btn"
            onClick={() => setDropdownOpen(o => !o)}
          >
            <span className="lang-dot" style={{ background: langIconColors[language] }} />
            <span>{currentLang.label} {currentLang.version}</span>
            <span className={`lang-chevron ${dropdownOpen ? 'open' : ''}`}>▼</span>
          </button>

          {dropdownOpen && (
            <div className="lang-dropdown">
              {LANGUAGES.map(lang => {
                const cfg = languageConfig[lang]
                return (
                  <div
                    key={lang}
                    id={`lang-option-${lang}`}
                    className={`lang-option ${lang === language ? 'active' : ''}`}
                    onClick={() => { onLanguageChange(lang); setDropdownOpen(false) }}
                  >
                    <div
                      className="lang-option-icon"
                      style={{
                        background: `${langIconColors[lang]}20`,
                        color: langIconColors[lang],
                        border: `1px solid ${langIconColors[lang]}40`
                      }}
                    >
                      {cfg.icon}
                    </div>
                    <span>{cfg.label}</span>
                    <span style={{ marginLeft: 'auto', fontSize: '11px', opacity: 0.6 }}>
                      {cfg.version}
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Right side */}
      <div className="navbar-right">
        <span className="session-timer">Session: {formatTime(sessionTime)}</span>

        {/* Theme toggle */}
        <button
          id="theme-toggle-btn"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          style={{
            width: 34, height: 34, borderRadius: '50%',
            background: 'var(--bg-elevated)', border: '1px solid var(--border-bright)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', fontSize: 16, transition: 'all 0.2s',
            color: theme === 'dark' ? '#FFB347' : '#1A1D23',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-primary)'; e.currentTarget.style.boxShadow = '0 0 12px rgba(79,255,176,0.2)' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-bright)'; e.currentTarget.style.boxShadow = 'none' }}
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>

        {/* Dedicated Logout Button */}
        <button
          id="logout-btn"
          onClick={onLogout}
          title="Logout"
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '6px 12px',
            background: 'transparent',
            border: '1px solid rgba(255,95,109,0.35)',
            borderRadius: 8,
            color: 'var(--accent-danger)',
            fontFamily: 'var(--font-body)',
            fontSize: 12,
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'rgba(255,95,109,0.08)'
            e.currentTarget.style.borderColor = 'rgba(255,95,109,0.6)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'transparent'
            e.currentTarget.style.borderColor = 'rgba(255,95,109,0.35)'
          }}
        >
          ⏏ Logout
        </button>

        {/* User Avatar — shows username */}
        <div
          id="user-avatar"
          onClick={() => setProfileOpen(o => !o)}
          style={{
            position: 'relative',
            width: 36, height: 36, borderRadius: '50%',
            background: `linear-gradient(135deg, hsl(${avatarHue},80%,55%) 0%, hsl(${(avatarHue + 60) % 360},70%,45%) 100%)`,
            border: '2px solid var(--border-bright)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 700,
            color: '#fff',
            cursor: 'pointer', transition: 'all 0.2s', userSelect: 'none',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-primary)'; e.currentTarget.style.boxShadow = '0 0 14px rgba(79,255,176,0.3)' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-bright)'; e.currentTarget.style.boxShadow = 'none' }}
        >
          {initials}

          {/* Profile dropdown */}
          {profileOpen && (
            <div style={{
              position: 'absolute', top: 'calc(100% + 10px)', right: 0,
              background: 'var(--bg-elevated)', border: '1px solid var(--border-bright)',
              borderRadius: 10, padding: 12, minWidth: 180,
              boxShadow: '0 16px 40px rgba(0,0,0,0.5)',
              zIndex: 200, fontFamily: 'var(--font-body)',
              animation: 'dropdown-in-right 0.15s ease-out',
              textAlign: 'left',
            }}>
              <div style={{ padding: '6px 8px 10px', borderBottom: '1px solid var(--border)' }}>
                <div style={{
                  fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2,
                }}>
                  {username || 'Student'}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>Logged in</div>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); setProfileOpen(false); onLogout() }}
                style={{
                  width: '100%', marginTop: 10, padding: '8px 10px',
                  background: 'rgba(255,95,109,0.08)', border: '1px solid rgba(255,95,109,0.25)',
                  borderRadius: 6, color: 'var(--accent-danger)',
                  fontFamily: 'var(--font-body)', fontSize: 13, fontWeight: 600,
                  cursor: 'pointer', textAlign: 'center', transition: 'all 0.15s',
                }}
              >
                ⏏ Sign out
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Close dropdowns on backdrop click */}
      {(dropdownOpen || profileOpen) && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 90 }}
          onClick={() => { setDropdownOpen(false); setProfileOpen(false) }}
        />
      )}
    </nav>
  )
}
