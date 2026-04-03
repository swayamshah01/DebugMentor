import { useState, useEffect } from 'react'
import { languageConfig } from '../data/mockData'
import { useTheme } from '../context/ThemeContext'

const LANGUAGES = ['python', 'cpp', 'java', 'javascript']

export default function Navbar({ language, onLanguageChange }) {
  const [dropdownOpen, setDropdownOpen] = useState(false)
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

  const currentLang = languageConfig[language]

  const langIconColors = {
    python: '#4B8BBE',
    cpp: '#659BD3',
    java: '#ED8B00',
    javascript: '#F7DF1E'
  }

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
                    onClick={() => {
                      onLanguageChange(lang)
                      setDropdownOpen(false)
                    }}
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

        {/* Theme toggle button */}
        <button
          id="theme-toggle-btn"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          style={{
            width: 34,
            height: 34,
            borderRadius: '50%',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-bright)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            fontSize: 16,
            transition: 'all 0.2s ease',
            color: theme === 'dark' ? '#FFB347' : '#1A1D23',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.borderColor = 'var(--accent-primary)'
            e.currentTarget.style.boxShadow = '0 0 12px rgba(79,255,176,0.2)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.borderColor = 'var(--border-bright)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>

        <div className="avatar-btn" id="user-avatar">
          RS
          <span className="avatar-tooltip">Student Profile</span>
        </div>
      </div>

      {/* Backdrop to close dropdown */}
      {dropdownOpen && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 90 }}
          onClick={() => setDropdownOpen(false)}
        />
      )}
    </nav>
  )
}
