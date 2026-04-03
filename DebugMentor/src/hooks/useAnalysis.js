import { useState, useCallback } from 'react'
import { detectScenario, runOutputMap } from '../data/mockData'

// =============================================
// useAnalysis — code-aware mock analysis engine
// Phase 2: swap setTimeout blocks for axios calls
// =============================================
export function useAnalysis() {
  const [isAnalyzing, setIsAnalyzing]   = useState(false)
  const [isRunning,   setIsRunning]     = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [runResult,   setRunResult]     = useState(null)
  const [detectedScenario, setDetectedScenario] = useState(null)

  /**
   * Run Code — simulates execution output.
   * Uses the last detected scenario's run output, or falls
   * back to the scenario that would be detected from `code`.
   */
  const runCode = useCallback((code, language) => {
    setIsRunning(true)
    setRunResult(null)
    // Phase 2: replace with axios.post('/api/run', { code, language })
    setTimeout(() => {
      const scenario = detectScenario(code)
      const langOutputs = runOutputMap[scenario.id] || runOutputMap.empty_array
      setRunResult(langOutputs[language] || langOutputs.python)
      setIsRunning(false)
    }, 800)
  }, [])

  /**
   * Submit for Analysis — detects patterns in `code` and
   * returns a contextually relevant mock result.
   * Phase 2: replace setTimeout with axios.post('/api/analyze', { code, language })
   */
  const submitForAnalysis = useCallback((code, language, onComplete) => {
    setIsAnalyzing(true)
    setAnalysisResult(null)
    setDetectedScenario(null)

    // Phase 2: replace with axios.post('/api/analyze', { code, language })
    setTimeout(() => {
      const scenario = detectScenario(code)
      setDetectedScenario(scenario)
      setAnalysisResult(scenario)
      setIsAnalyzing(false)
      if (onComplete) onComplete(scenario)
    }, 1600)
  }, [])

  const reset = useCallback(() => {
    setAnalysisResult(null)
    setRunResult(null)
    setDetectedScenario(null)
  }, [])

  return {
    isAnalyzing,
    isRunning,
    analysisResult,
    runResult,
    detectedScenario,
    runCode,
    submitForAnalysis,
    reset,
  }
}
