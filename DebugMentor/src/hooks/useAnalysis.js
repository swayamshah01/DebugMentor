/**
 * useAnalysis — API layer for DebugMentor
 *
 * Primary:  calls the real FastAPI backend at http://localhost:8000
 * Fallback: if the backend is unreachable, falls back to the local
 *           mock pattern-detector so the UI never breaks during development.
 *
 * Phase 2 wiring is already done — just keep the backend running.
 */

import { useState, useCallback } from 'react'
import axios from 'axios'
import { detectScenario, runOutputMap } from '../data/mockData'

const API_BASE = 'http://localhost:8000/api'

// ── Transform snake_case backend response → camelCase frontend shape ──────────
function transformAnalysis(backendResult) {
  if (!backendResult) return null
  return {
    // Match the shape HintsTab / TestCasesTab / StatusBar expect
    status:          backendResult.status,
    bugSummary:      backendResult.bug_summary,
    errorLine:       backendResult.error_line   ?? null,
    executionOutput: backendResult.execution_output ?? '',
    hints:           backendResult.hints      ?? [],
    testCases:       (backendResult.test_cases ?? []).map(tc => ({
      id:       tc.id,
      input:    tc.input,
      expected: tc.expected,
      actual:   tc.actual,
      passed:   tc.passed,
    })),
  }
}

// ── Hook ───────────────────────────────────────────────────────────────────────
export function useAnalysis() {
  const [isAnalyzing,    setIsAnalyzing]    = useState(false)
  const [isRunning,      setIsRunning]      = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [runResult,      setRunResult]      = useState(null)
  const [backendOnline,  setBackendOnline]  = useState(true)

  /**
   * runCode — POST /api/run
   * Real execution for Python; descriptive error for other languages.
   * Falls back to mock output if backend is unreachable.
   */
  const runCode = useCallback(async (code, language) => {
    setIsRunning(true)
    setRunResult(null)

    try {
      const { data } = await axios.post(`${API_BASE}/run`, { code, language }, {
        timeout: 15000,
      })
      setBackendOnline(true)
      setRunResult({
        success:  data.success,
        output:   data.output,
        execTime: data.exec_time,
      })
    } catch (err) {
      console.warn('[DebugMentor] Backend unreachable for /run — using mock output', err.message)
      setBackendOnline(false)
      // ── Fallback: use mock output map ──────────────────────────────────────
      const scenario   = detectScenario(code)
      const langOutputs = runOutputMap[scenario.id] || runOutputMap.empty_array
      setRunResult(langOutputs[language] || langOutputs.python)
    } finally {
      setIsRunning(false)
    }
  }, [])

  /**
   * submitForAnalysis — POST /api/submit
   * Gets real analysis from backend (Python: actual execution; others: pattern detection).
   * Falls back to local mock detector if backend is unreachable.
   */
  const submitForAnalysis = useCallback(async (code, language, onComplete) => {
    setIsAnalyzing(true)
    setAnalysisResult(null)

    try {
      const { data } = await axios.post(`${API_BASE}/submit`, {
        code,
        language,
        user_id: 1,   // Phase 2: use authenticated user ID from session
      }, {
        timeout: 30000,   // 30s — Python execution can take a few seconds
      })

      setBackendOnline(true)

      // data.analysis_result has the full structured result from the backend
      const result = transformAnalysis(data.analysis_result)
      setAnalysisResult(result)
      setIsAnalyzing(false)
      if (onComplete) onComplete(result)

    } catch (err) {
      console.warn('[DebugMentor] Backend unreachable for /submit — using mock', err.message)
      setBackendOnline(false)

      // ── Fallback: local pattern-based mock ────────────────────────────────
      // Small delay so the loading animation is visible
      await new Promise(r => setTimeout(r, 1200))
      const scenario = detectScenario(code)
      setAnalysisResult(scenario)
      setIsAnalyzing(false)
      if (onComplete) onComplete(scenario)
    }
  }, [])

  const reset = useCallback(() => {
    setAnalysisResult(null)
    setRunResult(null)
  }, [])

  return {
    isAnalyzing,
    isRunning,
    analysisResult,
    runResult,
    backendOnline,   // expose so UI can show a "using offline mode" badge if needed
    runCode,
    submitForAnalysis,
    reset,
  }
}
