/**
 * useAnalysis — API layer for DebugMentor (Phase 2)
 *
 * Primary:  calls the real FastAPI backend at http://localhost:8000.
 * Fallback: if the backend is unreachable, falls back to the local
 *           mock pattern-detector so the UI never breaks during development.
 *
 * Phase 2: transforms the new structured response (ast_issues, failure_report)
 * into the shape consumed by OutputPanel, TestCasesTab, StatusBar, HintsTab.
 */

import { useState, useCallback } from 'react'
import axios from 'axios'
import { detectScenario, runOutputMap } from '../data/mockData'

const API_BASE = 'http://localhost:8000/api'

// ── Transform Phase 2 backend response → frontend shape ──────────────────────
function transformPhase2Response(data) {
  if (!data) return null

  const astIssues = data.ast_issues || []
  const failureReport = data.failure_report || {}
  const testResults = failureReport.test_results || []

  // Build test cases for the TestCasesTab
  const testCases = testResults.map((tr, idx) => ({
    id: idx + 1,
    input: tr.input || '',
    label: tr.label || '',
    expected: tr.expected_output || '?',
    actual: tr.actual_output || tr.error_message || '(no output)',
    passed: tr.status === 'PASSED',
    status: tr.status,
    errorType: tr.error_type || null,
    executionTimeMs: tr.execution_time_ms || 0,
    isHidden: Boolean(tr.is_hidden),
  }))

  const passed = testCases.filter(t => t.passed).length
  const failed = testCases.filter(t => !t.passed).length
  const isClean = failed === 0 && astIssues.length === 0

  return {
    submissionId: data.id,
    status: isClean ? 'clean' : 'bugs_found',
    bugSummary: failureReport.failure_summary || '',
    errorLine: null,
    executionOutput: testResults.length > 0
      ? testResults.map(tr => tr.actual_output || tr.error_message || '').join('\n')
      : '',

    // Phase 3: the full LLM hints object
    hints: data.hints || null,

    // Phase 2: real test case results
    testCases,

    // Phase 2: AST findings for the StatusBar
    astIssues,

    // Failure report metadata
    failureReport,

    // Convenience counts
    passedCount: passed,
    failedCount: failed,
  }
}

// ── Hook ───────────────────────────────────────────────────────────────────────
export function useAnalysis(token, setToken) {
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
  const runCode = useCallback(async (code, language, options = {}) => {
    setIsRunning(true)
    setRunResult(null)

    try {
      const requestPayload = {
        code,
        language,
        problem_id: options.problemId ?? null,
        test_case_id: options.testCaseId ?? null,
        test_input: options.testInput ?? null,
      }

      const { data } = await axios.post(`${API_BASE}/run`, requestPayload, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        timeout: 15000,
      })
      setBackendOnline(true)
      setRunResult({
        success:  data.success,
        output:   data.output,
        execTime: data.exec_time,
      })
    } catch (err) {
      if (err.response?.status === 401 && setToken) {
        localStorage.removeItem('token')
        setToken(null)
        setIsRunning(false)
        return
      }
      if (err.response) {
        const detail = err.response.data?.detail || 'Run failed.'
        setRunResult({ success: false, output: detail, execTime: '—' })
        return
      }
      console.warn('[DebugMentor] Backend unreachable for /run — using mock output', err.message)
      setBackendOnline(false)
      // ── Fallback: use mock output map ──────────────────────────────────────
      const scenario   = detectScenario(code)
      const langOutputs = runOutputMap[scenario.id] || runOutputMap.empty_array
      setRunResult(langOutputs[language] || langOutputs.python)
    } finally {
      setIsRunning(false)
    }
  }, [token])

  /**
   * submitForAnalysis — POST /api/submit (Phase 2)
   * Gets real analysis: AST → Tests → Execute → Failure Detection.
   * Falls back to local mock detector if backend is unreachable.
   */
  const submitForAnalysis = useCallback(async (code, language, problemId = null, problemDesc = null, onComplete) => {
    setIsAnalyzing(true)
    setAnalysisResult(null)

    try {
      const { data } = await axios.post(`${API_BASE}/submit`, {
        code,
        language,
        test_input: "",
        problem_id: problemId,
        problem_desc: problemDesc
      }, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        timeout: 30000,   // 30s — execution can take a few seconds
      })

      setBackendOnline(true)

      // Transform Phase 2 structured response
      const result = transformPhase2Response(data)
      setAnalysisResult(result)

      // Sync execution result to the output panel
      const firstTest = (data.failure_report?.test_results || [])[0]
      if (firstTest) {
        setRunResult({
          success: firstTest.status === 'PASSED',
          output: firstTest.actual_output || firstTest.error_message || '(no output)',
          execTime: `${firstTest.execution_time_ms || 0}ms`,
        })
      }

      setIsAnalyzing(false)
      if (onComplete) onComplete(result)

    } catch (err) {
      if (err.response?.status === 401 && setToken) {
        localStorage.removeItem('token')
        setToken(null)
        setIsAnalyzing(false)
        return
      }
      if (err.response) {
        const detail = err.response.data?.detail || 'Submit failed.'
        setAnalysisResult({
          submissionId: null,
          status: 'error',
          bugSummary: detail,
          errorLine: null,
          executionOutput: detail,
          hints: null,
          testCases: [],
          astIssues: [],
          failureReport: { failure_summary: detail, test_results: [] },
          passedCount: 0,
          failedCount: 0,
        })
        setRunResult({ success: false, output: detail, execTime: '—' })
        setIsAnalyzing(false)
        return
      }

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
  }, [token])

  const reset = useCallback(() => {
    setAnalysisResult(null)
    setRunResult(null)
  }, [])

  const revealHint = useCallback(async (submissionId, userId = null) => {
    if (!submissionId) return null
    try {
      const { data } = await axios.post(`${API_BASE}/hint`, {
        submission_id: submissionId,
        user_id: userId
      }, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) }
      })
      return data
    } catch (err) {
      console.error('[DebugMentor] /hint error:', err)
      return null
    }
  }, [token])

  const generateAITestCases = useCallback(async (code, language, problemDesc = null) => {
    try {
      const { data } = await axios.post(`${API_BASE}/testcases/generate`, {
        code,
        language,
        problem_desc: problemDesc
      }, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        timeout: 20000
      })
      return data
    } catch (err) {
      console.error('[DebugMentor] /testcases/generate error:', err)
      return null
    }
  }, [token])

  const fetchProfile = useCallback(async (userId) => {
    try {
      const { data } = await axios.get(`${API_BASE}/profile/${userId}`, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        timeout: 10000
      })
      return data
    } catch (err) {
      console.error('[DebugMentor] /profile error:', err)
      return null
    }
  }, [token])

  const fetchPatterns = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/patterns`, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        timeout: 10000,
      })
      return data?.patterns || []
    } catch (err) {
      console.error('[DebugMentor] /patterns error:', err)
      return []
    }
  }, [token])

  const fetchPatternProblems = useCallback(async (patternId) => {
    try {
      const { data } = await axios.get(`${API_BASE}/patterns/${patternId}/problems`, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        timeout: 10000,
      })
      return data?.problems || []
    } catch (err) {
      console.error('[DebugMentor] /patterns/{id}/problems error:', err)
      return []
    }
  }, [token])

  const fetchProblemDetail = useCallback(async (problemId) => {
    try {
      const { data } = await axios.get(`${API_BASE}/problems/${problemId}`, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        timeout: 10000,
      })
      return data
    } catch (err) {
      console.error('[DebugMentor] /problems/{id} error:', err)
      return null
    }
  }, [token])

  return {
    isAnalyzing,
    isRunning,
    analysisResult,
    runResult,
    backendOnline,   // expose so UI can show a "using offline mode" badge if needed
    runCode,
    submitForAnalysis,
    revealHint,
    generateAITestCases,
    fetchProfile,
    fetchPatterns,
    fetchPatternProblems,
    fetchProblemDetail,
    reset,
  }
}
