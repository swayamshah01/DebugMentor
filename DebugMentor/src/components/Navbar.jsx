import { useTheme } from '../context/useTheme'
import { languageConfig } from '../data/languages'


export default function Navbar({
  username,
  screen,
  problem,
  language,
  availableLanguages,
  onLanguageChange,
  onBack,
  onProfile,
  onLogout,
}) {
  const { theme, toggleTheme } = useTheme()
  const initial = (username || 'U').slice(0, 1).toUpperCase()
  const showBack = screen !== 'explorer'

  return (
    <header className="topbar">
      <div className="topbar-left">
        {showBack && (
          <button className="button button-quiet back-button" type="button" onClick={onBack}>
            Back
          </button>
        )}
        <button className="brand-button" type="button" onClick={onBack} aria-label="Open practice patterns">
          <span className="brand-mark">DM</span>
          <span className="brand-name">DebugMentor</span>
        </button>
        {screen === 'workspace' && problem && (
          <span className="topbar-problem">{problem.title}</span>
        )}
      </div>

      <div className="topbar-actions">
        {screen === 'workspace' && availableLanguages.length > 0 && (
          <label className="language-select">
            <span className="sr-only">Language</span>
            <select value={language} onChange={(event) => onLanguageChange(event.target.value)}>
              {availableLanguages.map((item) => (
                <option key={item} value={item}>{languageConfig[item]?.label || item}</option>
              ))}
            </select>
          </label>
        )}
        <button className="button button-quiet" type="button" onClick={toggleTheme}>
          {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
        <button className="profile-button" type="button" onClick={onProfile} aria-label="Open profile">
          <span>{initial}</span>
          <strong>{username || 'Profile'}</strong>
        </button>
        <button className="button button-quiet logout-button" type="button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </header>
  )
}
