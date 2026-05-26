import { useEffect, useMemo, useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import StatusBar from './components/StatusBar'
import Auth from './components/Auth'
import LandingPage from './components/LandingPage'
import { ProfileDashboard } from './components/ProfileDashboard'
import PatternExplorerPage from './components/PatternExplorerPage'
import ProblemWorkspace from './components/ProblemWorkspace'
import { useAnalysis } from './hooks/useAnalysis'

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [username, setUsername] = useState(() => {
    const t = localStorage.getItem('token')
    if (!t) return null
    try {
      const payload = JSON.parse(atob(t.split('.')[1]))
      return payload.username || localStorage.getItem('username') || null
    } catch {
      return localStorage.getItem('username') || null
    }
  })
  const [userId, setUserId] = useState(() => {
    const t = localStorage.getItem('token')
    if (!t) return null
    try {
      const payload = JSON.parse(atob(t.split('.')[1]))
      return payload.sub || payload.user_id || null
    } catch {
      return null
    }
  })
  const [screen, setScreen] = useState(() => token ? 'explorer' : 'landing')
  const [profileOpen, setProfileOpen] = useState(false)

  const [patterns, setPatterns] = useState([])
  const [patternsLoading, setPatternsLoading] = useState(false)
  const [expandedPatternId, setExpandedPatternId] = useState(null)
  const [patternProblemsById, setPatternProblemsById] = useState({})
  const [patternLoadingId, setPatternLoadingId] = useState(null)
  const [selectedProblemId, setSelectedProblemId] = useState(null)
  const [selectedProblemDetail, setSelectedProblemDetail] = useState(null)
  const [problemLoading, setProblemLoading] = useState(false)
  const [profileData, setProfileData] = useState(null)
  const [selectedVisibleTestCaseId, setSelectedVisibleTestCaseId] = useState(null)

  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState('')
  const [activeTab, setActiveTab] = useState('hints')

  // ── Analysis hook ────────────────────────────────────────
  const {
    isAnalyzing,
    isRunning,
    analysisResult,
    runResult,
    backendOnline,
    runCode,
    submitForAnalysis,
    revealHint,
    fetchProfile,
    fetchPatterns,
    fetchPatternProblems,
    fetchProblemDetail,
    reset,
  } = useAnalysis(token, setToken)

  const profilePatternSummary = useMemo(() => {
    const summary = {}
    if (profileData?.weak_patterns) {
      profileData.weak_patterns.forEach(item => {
        summary[item.pattern_id] = item
      })
    }
    return summary
  }, [profileData])

  const expandedPatternProblems = patternProblemsById[expandedPatternId] || []

  const selectedVisibleTestCase = useMemo(() => {
    if (!selectedProblemDetail?.test_cases?.length) return null
    return selectedProblemDetail.test_cases.find(testCase => testCase.id === selectedVisibleTestCaseId) || selectedProblemDetail.test_cases[0]
  }, [selectedProblemDetail, selectedVisibleTestCaseId])

  const handleTokenSet = useCallback((newToken) => {
    setToken(newToken)
    if (newToken) {
      try {
        const payload = JSON.parse(atob(newToken.split('.')[1]))
        setUserId(payload.sub || payload.user_id || null)
      } catch {
        console.warn('Failed to extract user_id from token')
      }
    }
    setScreen('explorer')
  }, [])

  const handleLogout = useCallback(() => {
    if (!window.confirm('Are you sure you want to logout?')) return
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setToken(null)
    setUsername(null)
    setUserId(null)
    setExpandedPatternId(null)
    setPatternProblemsById({})
    setSelectedProblemId(null)
    setSelectedProblemDetail(null)
    setSelectedVisibleTestCaseId(null)
    setProfileData(null)
    setScreen('landing')
  }, [])

  const loadProblem = useCallback(async (problemId) => {
    if (!problemId) return
    setProblemLoading(true)
    setSelectedProblemDetail(null)
    setCode('')
    reset()
    const detail = await fetchProblemDetail(problemId)
    setSelectedProblemDetail(detail)
    const starterForLanguage = detail?.starter_code_map?.[language] || detail?.starter_code || ''
    if (starterForLanguage) {
      setCode(starterForLanguage)
    }
    const firstVisible = detail?.test_cases?.[0]
    setSelectedVisibleTestCaseId(firstVisible?.id ?? null)
    setProblemLoading(false)
  }, [fetchProblemDetail, language, reset])

  const handleTogglePattern = useCallback((patternId) => {
    setExpandedPatternId(current => (current === patternId ? null : patternId))
  }, [])

  const handleProblemSelect = useCallback((problemId) => {
    setSelectedProblemId(problemId)
    setScreen('workspace')
  }, [])

  const handleLanguageChange = useCallback((lang) => {
    setLanguage(lang)
    const starterForLanguage = selectedProblemDetail?.starter_code_map?.[lang]
    if (starterForLanguage) {
      setCode(starterForLanguage)
    }
  }, [selectedProblemDetail])

  const handleCodeChange = useCallback((val) => setCode(val || ''), [])

  const handleRun = useCallback(() => {
    if (!code.trim()) return

    if (selectedProblemDetail) {
      setActiveTab('output')
      runCode(code, language, {
        problemId: selectedProblemDetail.id,
        testCaseId: selectedVisibleTestCase?.id ?? null,
        testInput: selectedVisibleTestCase?.input ?? '',
      })
      return
    }

    setActiveTab('output')
    runCode(code, language)
  }, [code, language, runCode, selectedProblemDetail, selectedVisibleTestCase])

  const handleSubmit = useCallback(() => {
    if (!code.trim()) return
    setActiveTab('tests')
    if (!selectedProblemDetail) return
    submitForAnalysis(code, language, selectedProblemDetail.id, selectedProblemDetail?.statement || '')
  }, [code, language, selectedProblemDetail, submitForAnalysis])

  const handleSelectVisibleTestCase = useCallback((testCase) => {
    setSelectedVisibleTestCaseId(testCase?.id ?? null)
  }, [])

  const handleBackToExplorer = useCallback(() => {
    setScreen('explorer')
  }, [])

  const ensurePatternProblems = useCallback(async (patternId) => {
    if (!patternId || patternProblemsById[patternId]) return
    setPatternLoadingId(patternId)
    const items = await fetchPatternProblems(patternId)
    setPatternProblemsById(current => ({ ...current, [patternId]: items }))
    setPatternLoadingId(null)
  }, [fetchPatternProblems, patternProblemsById])

  useEffect(() => {
    if (!token || screen === 'landing') return

    const loadPatterns = async () => {
      setPatternsLoading(true)
      const items = await fetchPatterns()
      setPatterns(items)
      setPatternsLoading(false)
    }

    loadPatterns()
  }, [screen, token, fetchPatterns])

  useEffect(() => {
    if (screen !== 'explorer' || !expandedPatternId) return
    ensurePatternProblems(expandedPatternId)
  }, [screen, expandedPatternId, ensurePatternProblems])

  useEffect(() => {
    if (screen !== 'workspace' || !selectedProblemId) return
    loadProblem(selectedProblemId)
  }, [screen, selectedProblemId, loadProblem])

  useEffect(() => {
    if (!profileOpen || !userId) return
    const load = async () => {
      const data = await fetchProfile(userId)
      setProfileData(data)
    }
    load()
  }, [profileOpen, userId, fetchProfile])

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

  if (!token) {
    return <LandingPage onGetStarted={() => setScreen('auth')} />
  }

  return (
    <div className="app-shell">
      <Navbar
        language={language}
        onLanguageChange={handleLanguageChange}
        backendOnline={backendOnline}
        username={username}
        onLogout={handleLogout}
        onProfileOpen={() => setProfileOpen(true)}
      />

      {screen === 'explorer' ? (
        <PatternExplorerPage
          patterns={patterns}
          loading={patternsLoading}
          expandedPatternId={expandedPatternId}
          patternProblemsById={patternProblemsById}
          loadingPatternId={patternLoadingId}
          onTogglePattern={handleTogglePattern}
          onSelectProblem={handleProblemSelect}
        />
      ) : (
        <ProblemWorkspace
          problem={selectedProblemDetail}
          code={code}
          language={language}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isAnalyzing={isAnalyzing}
          isRunning={isRunning}
          runResult={runResult}
          analysisResult={analysisResult}
          onBack={handleBackToExplorer}
          onCodeChange={handleCodeChange}
          onRun={handleRun}
          onSubmit={handleSubmit}
          revealHint={revealHint}
          selectedVisibleTestCaseId={selectedVisibleTestCaseId}
          onSelectVisibleTestCase={handleSelectVisibleTestCase}
          loading={problemLoading}
        />
      )}

      <StatusBar
        language={language}
        isAnalyzing={isAnalyzing}
        analysisResult={analysisResult}
      />

      {profileOpen && userId && (
        <ProfileDashboard
          userId={userId}
          fetchProfile={fetchProfile}
          token={token}
          onClose={() => setProfileOpen(false)}
        />
      )}
    </div>
  )
}
