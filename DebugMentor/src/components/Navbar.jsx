import { useEffect, useState } from 'react'
import { languageConfig } from '../data/languages'
import { useTheme } from '../context/ThemeContext'

const LANGUAGES = ['python', 'cpp', 'java', 'javascript']

const langIconColors = {
  python: '#3b82f6',
  cpp: '#6366f1',
  java: '#c2410c',
  javascript: '#ca8a04',
}

export default function Navbar({
  language,
  onLanguageChange,
  backendOnline = true,
  username,
  onLogout,
  onProfileOpen,
  showBackToPatterns = false,
  onBackToPatterns,
  problem,
}) {
  const [langDropdownOpen, setLangDropdownOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [sessionTime, setSessionTime] = useState(0)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    const interval = setInterval(() => setSessionTime((t) => t + 1), 1000)
    return () => clearInterval(interval)
  }, [])

  const formatTime = (s) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m}m ${String(sec).padStart(2, '0')}s`
  }

  const initials = username ? username.slice(0, 2).toUpperCase() : 'DM'
  const currentLang = languageConfig[language]

  return (
    <nav className="navbar">
      <a className="navbar-logo" href="#" onClick={(e) => e.preventDefault()}>
        <div className="navbar-logo-icon">DM</div>
        <span className="navbar-logo-text">Debug<span>Mentor</span></span>
      </a>

      {showBackToPatterns && (
        <button type="button" className="navbar-back-btn" onClick={onBackToPatterns}>
          Back
        </button>
      )}

      {showBackToPatterns && problem && (
        <div className="navbar-breadcrumb">
          <span>{problem.pattern?.name || 'Pattern'}</span>
          <span>/</span>
          <strong>{problem.title}</strong>
        </div>
      )}

      <div className={`connection-pill ${backendOnline ? 'live' : 'offline'}`}>
        <span className="connection-dot" />
        {backendOnline ? 'API Live' : 'Offline Mode'}
      </div>

      <div className="navbar-center">
        <div className="lang-selector-wrapper">
          <button
            id="lang-selector-btn"
            className="lang-selector-btn"
            onClick={() => setLangDropdownOpen((o) => !o)}
          >
            <span className="lang-dot" style={{ background: langIconColors[language] }} />
            <span>{currentLang.label} {currentLang.version}</span>
            <span className={`lang-chevron ${langDropdownOpen ? 'open' : ''}`}>v</span>
          </button>

          {langDropdownOpen && (
            <div className="lang-dropdown">
              {LANGUAGES.map((lang) => {
                const cfg = languageConfig[lang]
                return (
                  <div
                    key={lang}
                    id={`lang-option-${lang}`}
                    className={`lang-option ${lang === language ? 'active' : ''}`}
                    onClick={() => {
                      onLanguageChange(lang)
                      setLangDropdownOpen(false)
                    }}
                  >
                    <div
                      className="lang-option-icon"
                      style={{
                        background: `${langIconColors[lang]}18`,
                        color: langIconColors[lang],
                        border: `1px solid ${langIconColors[lang]}35`,
                      }}
                    >
                      {cfg.icon}
                    </div>
                    <span>{cfg.label}</span>
                    <span style={{ marginLeft: 'auto', fontSize: '11px', opacity: 0.65 }}>
                      {cfg.version}
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      <div className="navbar-right">
        <div className="navbar-utility-group">
          <span className="session-timer">Session: {formatTime(sessionTime)}</span>

          <button
            id="theme-toggle-btn"
            className="theme-toggle-btn"
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? 'Light' : 'Dark'}
          </button>

          <button id="logout-btn" className="logout-btn" onClick={onLogout} title="Logout">
            Logout
          </button>
        </div>

        <div
          id="user-avatar"
          className="user-avatar"
          onClick={() => setProfileOpen((o) => !o)}
        >
          {initials}

          {profileOpen && (
            <div className="profile-dropdown">
              <div className="profile-dropdown-header">
                <div className="profile-dropdown-name">{username || 'Student'}</div>
                <div className="profile-dropdown-meta">Logged in</div>
              </div>

              <button
                className="profile-dropdown-action primary"
                onClick={(e) => {
                  e.stopPropagation()
                  setProfileOpen(false)
                  onProfileOpen && onProfileOpen()
                }}
              >
                View Profile
              </button>

              <button
                className="profile-dropdown-action danger"
                onClick={(e) => {
                  e.stopPropagation()
                  setProfileOpen(false)
                  onLogout()
                }}
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>

      {(langDropdownOpen || profileOpen) && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 90 }}
          onClick={() => {
            setLangDropdownOpen(false)
            setProfileOpen(false)
          }}
        />
      )}
    </nav>
  )
}
