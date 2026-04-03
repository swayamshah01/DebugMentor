import { useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import CodeEditorPanel from './components/CodeEditorPanel'
import OutputPanel from './components/OutputPanel'
import StatusBar from './components/StatusBar'
import { starterCode, getDisplayCode, wrapInBoilerplate } from './data/mockData'
import { useAnalysis } from './hooks/useAnalysis'

export default function App() {
  // ── Core state ──────────────────────────────────────────
  const [language,    setLanguage]    = useState('python')
  const [focusedCode, setFocusedCode] = useState(starterCode.python.focused)
  const [editorMode,  setEditorMode]  = useState('focused')  // 'focused' | 'complete'
  const [activeTab,   setActiveTab]   = useState('hints')
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

  // ── Computed display code for Monaco ─────────────────────
  // In 'focused' mode: show just the function
  // In 'complete' mode: show the full wrapped boilerplate (read-only)
  const displayCode = getDisplayCode(language, editorMode, focusedCode)

  // ── Handlers ─────────────────────────────────────────────
  const handleLanguageChange = useCallback((lang) => {
    setLanguage(lang)
    setFocusedCode(starterCode[lang].focused)
    setEditorMode('focused')  // reset to focused when language changes
  }, [])

  const handleCodeChange = useCallback((val) => {
    // Only update when in focused mode (complete mode is read-only)
    setFocusedCode(val || '')
  }, [])

  const handleModeChange = useCallback((newMode) => {
    setEditorMode(newMode)
  }, [])

  const handleRun = useCallback(() => {
    setActiveTab('output')
    // Always run the fully wrapped code
    const finalCode = editorMode === 'focused'
      ? wrapInBoilerplate(focusedCode, language)
      : focusedCode
    runCode(finalCode, language)
  }, [editorMode, focusedCode, language, runCode])

  const handleSubmit = useCallback(() => {
    setActiveTab('hints')
    setRevealedHints(0)
    // Always submit the full code — backend always receives a valid, runnable script
    const finalCode = editorMode === 'focused'
      ? wrapInBoilerplate(focusedCode, language)
      : focusedCode
    submitForAnalysis(finalCode, language, (scenario) => {
      setRevealedHints(scenario?.status === 'clean' ? 3 : 1)
    })
  }, [editorMode, focusedCode, language, submitForAnalysis])

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
          code={displayCode}
          language={language}
          editorMode={editorMode}
          isAnalyzing={isAnalyzing}
          isRunning={isRunning}
          onCodeChange={handleCodeChange}
          onRun={handleRun}
          onSubmit={handleSubmit}
          onModeChange={handleModeChange}
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
        editorMode={editorMode}
        isAnalyzing={isAnalyzing}
        analysisResult={analysisResult}
      />
    </div>
  )
}
