import { useCallback, useEffect, useMemo, useState } from 'react'

import Auth from './components/Auth'
import Navbar from './components/Navbar'
import PatternExplorerPage from './components/PatternExplorerPage'
import ProblemWorkspace from './components/ProblemWorkspace'
import ProfileDashboard from './components/ProfileDashboard'
import { usePractice } from './hooks/usePractice'


function readIdentity(token) {
  if (!token) return { userId: null, username: null }
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return { userId: Number(payload.sub), username: payload.username || null }
  } catch {
    return { userId: null, username: null }
  }
}


export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [identity, setIdentity] = useState(() => readIdentity(localStorage.getItem('token')))
  const [screen, setScreen] = useState('explorer')
  const [patterns, setPatterns] = useState([])
  const [expandedPatternId, setExpandedPatternId] = useState(null)
  const [problemsByPattern, setProblemsByPattern] = useState({})
  const [loadingPatternId, setLoadingPatternId] = useState(null)
  const [catalogLoading, setCatalogLoading] = useState(() => Boolean(localStorage.getItem('token')))
  const [problemLoading, setProblemLoading] = useState(false)
  const [problem, setProblem] = useState(null)
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState('')
  const [drafts, setDrafts] = useState({})
  const [selectedTestCaseId, setSelectedTestCaseId] = useState(null)
  const [activePanel, setActivePanel] = useState('tests')
  const [profile, setProfile] = useState(null)

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setToken(null)
    setIdentity({ userId: null, username: null })
    setPatterns([])
    setProblem(null)
    setProfile(null)
    setScreen('explorer')
  }, [])

  const {
    busyAction,
    gradeResult,
    submissionResult,
    hints,
    requestError,
    hintError,
    runSolution,
    submitSolution: submitOfficialSolution,
    requestNextHint,
    resetPractice,
    fetchPatterns,
    fetchPatternProblems,
    fetchProblem,
    fetchProfile,
  } = usePractice(token, logout)

  const selectedTestCase = useMemo(() => (
    problem?.test_cases?.find((testCase) => testCase.id === selectedTestCaseId)
      || problem?.test_cases?.[0]
      || null
  ), [problem, selectedTestCaseId])

  const refreshProfile = useCallback(async () => {
    if (!identity.userId) return
    const data = await fetchProfile(identity.userId)
    if (data) setProfile(data)
  }, [fetchProfile, identity.userId])

  useEffect(() => {
    if (!token) return
    let cancelled = false

    const load = async () => {
      const [catalog, profileData] = await Promise.all([
        fetchPatterns(),
        identity.userId ? fetchProfile(identity.userId) : null,
      ])
      if (!cancelled) {
        setPatterns(catalog)
        if (profileData) setProfile(profileData)
        setCatalogLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [fetchPatterns, fetchProfile, identity.userId, token])

  const handleAuthenticated = useCallback((nextToken) => {
    localStorage.setItem('token', nextToken)
    setToken(nextToken)
    setIdentity(readIdentity(nextToken))
    setCatalogLoading(true)
    setScreen('explorer')
  }, [])

  const togglePattern = useCallback(async (patternId) => {
    if (expandedPatternId === patternId) {
      setExpandedPatternId(null)
      return
    }
    setExpandedPatternId(patternId)
    if (problemsByPattern[patternId]) return
    setLoadingPatternId(patternId)
    const items = await fetchPatternProblems(patternId)
    setProblemsByPattern((current) => ({ ...current, [patternId]: items }))
    setLoadingPatternId(null)
  }, [expandedPatternId, fetchPatternProblems, problemsByPattern])

  const openProblem = useCallback(async (problemId) => {
    setScreen('workspace')
    setProblemLoading(true)
    setProblem(null)
    resetPractice()
    const detail = await fetchProblem(problemId)
    if (detail) {
      const available = detail.available_languages || []
      const nextLanguage = available.includes(language) ? language : (available[0] || 'python')
      const draftKey = `${detail.id}:${nextLanguage}`
      setProblem(detail)
      setLanguage(nextLanguage)
      setCode(drafts[draftKey] ?? detail.starter_code_map?.[nextLanguage] ?? '')
      setSelectedTestCaseId(detail.test_cases?.[0]?.id ?? null)
      setActivePanel('tests')
    }
    setProblemLoading(false)
  }, [drafts, fetchProblem, language, resetPractice])

  const changeLanguage = useCallback((nextLanguage) => {
    if (!problem) return
    setDrafts((current) => ({ ...current, [`${problem.id}:${language}`]: code }))
    setLanguage(nextLanguage)
    setCode(drafts[`${problem.id}:${nextLanguage}`] ?? problem.starter_code_map?.[nextLanguage] ?? '')
    resetPractice()
    setActivePanel('tests')
  }, [code, drafts, language, problem, resetPractice])

  const changeCode = useCallback((nextCode) => {
    const value = nextCode || ''
    setCode(value)
    if (problem) {
      setDrafts((current) => ({ ...current, [`${problem.id}:${language}`]: value }))
    }
  }, [language, problem])

  const runSelectedCase = useCallback(async () => {
    if (!problem || !selectedTestCase || !code.trim()) return
    const result = await runSolution({
      code,
      language,
      problemId: problem.id,
      testCaseId: selectedTestCase.id,
    })
    if (result) setActivePanel('result')
  }, [code, language, problem, runSolution, selectedTestCase])

  const submitSolution = useCallback(async () => {
    if (!problem || !code.trim()) return
    const result = await submitOfficialSolution({ code, language, problemId: problem.id })
    if (result) {
      setActivePanel(result.success ? 'result' : 'hints')
      refreshProfile()
    }
  }, [code, language, problem, refreshProfile, submitOfficialSolution])

  if (!token) {
    return <Auth onAuthenticated={handleAuthenticated} />
  }

  return (
    <div className="app-shell">
      <Navbar
        username={identity.username}
        screen={screen}
        problem={problem}
        language={language}
        availableLanguages={problem?.available_languages || []}
        onLanguageChange={changeLanguage}
        onBack={() => setScreen('explorer')}
        onProfile={() => setScreen('profile')}
        onLogout={logout}
      />

      {screen === 'explorer' && (
        <PatternExplorerPage
          patterns={patterns}
          loading={catalogLoading}
          expandedPatternId={expandedPatternId}
          problemsByPattern={problemsByPattern}
          loadingPatternId={loadingPatternId}
          profile={profile}
          onTogglePattern={togglePattern}
          onSelectProblem={openProblem}
        />
      )}

      {screen === 'workspace' && (
        <ProblemWorkspace
          problem={problem}
          loading={problemLoading}
          code={code}
          language={language}
          selectedTestCase={selectedTestCase}
          selectedTestCaseId={selectedTestCaseId}
          activePanel={activePanel}
          busyAction={busyAction}
          gradeResult={gradeResult}
          submissionResult={submissionResult}
          hints={hints}
          requestError={requestError}
          hintError={hintError}
          onCodeChange={changeCode}
          onRun={runSelectedCase}
          onSubmit={submitSolution}
          onPanelChange={setActivePanel}
          onSelectTestCase={(testCase) => setSelectedTestCaseId(testCase.id)}
          onRequestHint={requestNextHint}
        />
      )}

      {screen === 'profile' && (
        <ProfileDashboard
          profile={profile}
          loading={!profile}
          onRefresh={refreshProfile}
          onPractice={() => setScreen('explorer')}
        />
      )}
    </div>
  )
}
