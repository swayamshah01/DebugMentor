import { useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import CodeEditorPanel from './components/CodeEditorPanel'
import OutputPanel from './components/OutputPanel'
import StatusBar from './components/StatusBar'
import { starterCode, getDisplayCode, wrapInBoilerplate } from './data/mockData'
import { useAnalysis } from './hooks/useAnalysis'

export default function App() {
  // ── Core state ──────────────────────────────────────────
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
  } = useAnalysis()

  // ── Handlers ─────────────────────────────────────────────
  const handleLanguageChange = useCallback((lang) => {
    setLanguage(lang)
    setCode(wrapInBoilerplate(starterCode[lang].focused, lang))
  }, [])

  const handleCodeChange = useCallback((val) => {
    setCode(val || '')
  }, [])

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
      if (next >= 3) {
        setShowSolutionModal(true)
        return prev
      }
      return next
    })
  }, [])

  const handleRevealSolution = useCallback(() => {
    setShowSolutionModal(false)
    setRevealedHints(3)
  }, [])

  return (
    <div className="app-shell">
      {/* ── Navbar ── */}
      <Navbar
        language={language}
        onLanguageChange={handleLanguageChange}
        backendOnline={backendOnline}
      />

      {/* ── Main workspace ── */}
      <div className="main-workspace">
        {/* Left: Code Editor */}
        <CodeEditorPanel
          code={code}
          language={language}
          isAnalyzing={isAnalyzing}
          isRunning={isRunning}
          onCodeChange={handleCodeChange}
          onRun={handleRun}
          onSubmit={handleSubmit}
        />

        {/* Divider */}
        <div className="panel-divider" />

        {/* Right: Output / Hints / Tests */}
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

      {/* ── Status Bar ── */}
      <StatusBar
        language={language}
        isAnalyzing={isAnalyzing}
        analysisResult={analysisResult}
      />
    </div>
  )
}
