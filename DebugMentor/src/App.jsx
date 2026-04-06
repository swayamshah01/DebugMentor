import { useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import CodeEditorPanel from './components/CodeEditorPanel'
import OutputPanel from './components/OutputPanel'
import StatusBar from './components/StatusBar'
import Auth from './components/Auth'
import LandingPage from './components/LandingPage'
import { starterCode, wrapInBoilerplate } from './data/mockData'
import { useAnalysis } from './hooks/useAnalysis'

// ── Screens ───────────────────────────────────────────────────
// 'landing' → 'auth' → 'app'

export default function App() {
  // ── Auth / navigation state ──────────────────────────────
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [username, setUsername] = useState(() => {
    // Try to decode username from stored token
    const t = localStorage.getItem('token')
    if (!t) return null
    try {
      const payload = JSON.parse(atob(t.split('.')[1]))
      return payload.username || localStorage.getItem('username') || null
    } catch {
      return localStorage.getItem('username') || null
    }
  })
  // If token exists, go straight to 'app'. Otherwise show 'landing'.
  const [screen, setScreen] = useState(() => token ? 'app' : 'landing')

  // ── Core editor state ────────────────────────────────────
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState(() => wrapInBoilerplate(starterCode.python.focused, 'python'))
  const [activeTab, setActiveTab] = useState('hints')
  const [revealedHints, setRevealedHints] = useState(0)
  const [showSolutionModal, setShowSolutionModal] = useState(false)

  // ── Analysis hook ────────────────────────────────────────
  const {
    isAnalyzing,
    isRunning,
    analysisResult,
    runResult,
    backendOnline,
    runCode,
    submitForAnalysis,
  } = useAnalysis(token, setToken)

  // ── Auth handlers ─────────────────────────────────────────
  const handleTokenSet = useCallback((newToken) => {
    setToken(newToken)
    setScreen('app')
  }, [])

  const handleLogout = useCallback(() => {
    if (!window.confirm('Are you sure you want to logout?')) return
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setToken(null)
    setUsername(null)
    setScreen('landing')
  }, [])

  // ── Editor handlers ───────────────────────────────────────
  const handleLanguageChange = useCallback((lang) => {
    setLanguage(lang)
    setCode(wrapInBoilerplate(starterCode[lang].focused, lang))
  }, [])

  const handleCodeChange = useCallback((val) => setCode(val || ''), [])

  const handleRun = useCallback(() => {
    setActiveTab('output')
    runCode(code, language)
  }, [code, language, runCode])

  const handleSubmit = useCallback(() => {
    setActiveTab('hints')
    setRevealedHints(0)
    submitForAnalysis(code, language, (scenario) => {
      setRevealedHints(scenario?.status === 'clean' ? 3 : 1)
    })
  }, [code, language, submitForAnalysis])

  const handleNextHint = useCallback(() => {
    setRevealedHints(prev => {
      const next = prev + 1
      if (next >= 3) { setShowSolutionModal(true); return prev }
      return next
    })
  }, [])

  const handleRevealSolution = useCallback(() => {
    setShowSolutionModal(false)
    setRevealedHints(3)
  }, [])

  // ── Screen routing ────────────────────────────────────────
  if (screen === 'landing') {
    return <LandingPage onGetStarted={() => setScreen('auth')} />
  }

  if (screen === 'auth') {
    return (
      <Auth
        setToken={handleTokenSet}
        setUsername={setUsername}
        onBackToLanding={() => setScreen('landing')}
      />
    )
  }

  // ── Main IDE ──────────────────────────────────────────────
  return (
    <div className="app-shell">
      <Navbar
        language={language}
        onLanguageChange={handleLanguageChange}
        backendOnline={backendOnline}
        username={username}
        onLogout={handleLogout}
      />

      <div className="main-workspace">
        <CodeEditorPanel
          code={code}
          language={language}
          isAnalyzing={isAnalyzing}
          isRunning={isRunning}
          onCodeChange={handleCodeChange}
          onRun={handleRun}
          onSubmit={handleSubmit}
        />
        <div className="panel-divider" />
        <OutputPanel
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          analysisResult={analysisResult}
          isAnalyzing={isAnalyzing}
          isRunning={isRunning}
          runResult={runResult}
          revealedHints={revealedHints}
          showSolutionModal={showSolutionModal}
          onNextHint={handleNextHint}
          onShowSolutionModal={() => setShowSolutionModal(true)}
          onCancelModal={() => setShowSolutionModal(false)}
          onRevealSolution={handleRevealSolution}
        />
      </div>

      <StatusBar
        language={language}
        isAnalyzing={isAnalyzing}
        analysisResult={analysisResult}
      />
    </div>
  )
}
