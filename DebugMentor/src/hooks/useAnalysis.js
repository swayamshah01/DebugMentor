import { useState, useCallback } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

function transformSubmissionResponse(data) {
  if (!data) return null

  const astIssues = data.ast_issues || []
  const failureReport = data.failure_report || {}
  const testResults = failureReport.test_results || []

  const testCases = testResults.map((result, index) => ({
    id: index + 1,
    input: result.input || '',
    label: result.label || '',
    expected: result.expected_output || '?',
    actual: result.actual_output || result.error_message || '(no output)',
    passed: result.status === 'PASSED',
    status: result.status,
    errorType: result.error_type || null,
    executionTimeMs: result.execution_time_ms || 0,
    isHidden: Boolean(result.is_hidden),
  }))

  const passed = testCases.filter((testCase) => testCase.passed).length
  const failed = testCases.length - passed
  const isClean = failed === 0 && astIssues.length === 0

  return {
    submissionId: data.id,
    status: isClean ? 'clean' : 'bugs_found',
    bugSummary: failureReport.failure_summary || '',
    errorLine: null,
    executionOutput: testResults.length > 0
      ? testResults.map((result) => result.actual_output || result.error_message || '').join('\n')
      : '',
    hints: data.hints || null,
    testCases,
    astIssues,
    failureReport,
    passedCount: passed,
    failedCount: failed,
  }
}

function buildOfflineResult(message) {
  return {
    submissionId: null,
    status: 'error',
    bugSummary: message,
    errorLine: null,
    executionOutput: message,
    hints: null,
    testCases: [],
    astIssues: [],
    failureReport: {
      failure_summary: message,
      test_results: [],
    },
    passedCount: 0,
    failedCount: 0,
  }
}

export function useAnalysis(token, setToken) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [runResult, setRunResult] = useState(null)
  const [backendOnline, setBackendOnline] = useState(true)

  const authHeaders = useCallback(() => (
    token ? { Authorization: `Bearer ${token}` } : {}
  ), [token])

  const handleUnauthorized = useCallback((err) => {
    if (err.response?.status !== 401 || !setToken) return false
    localStorage.removeItem('token')
    setToken(null)
    return true
  }, [setToken])

  const runCode = useCallback(async (code, language, options = {}) => {
    setIsRunning(true)
    setRunResult(null)

    try {
      const { data } = await axios.post(`${API_BASE}/run`, {
        code,
        language,
        problem_id: options.problemId ?? null,
        test_case_id: options.testCaseId ?? null,
        test_input: options.testInput ?? null,
      }, {
        headers: authHeaders(),
        timeout: 15000,
      })

      setBackendOnline(true)
      setRunResult({
        success: data.success,
        output: data.output,
        execTime: data.exec_time,
        totalTests: data.total_tests || 0,
        passedTests: data.passed_tests || 0,
        failedTests: data.failed_tests || 0,
        dominantFailureType: data.dominant_failure_type || null,
        testCases: (data.test_results || []).map((result, index) => ({
          id: index + 1,
          input: result.input || '',
          label: result.label || '',
          expected: result.expected_output || '?',
          actual: result.actual_output || result.error_message || '(no output)',
          passed: result.status === 'PASSED',
          status: result.status,
          errorType: result.error_type || null,
          executionTimeMs: result.execution_time_ms || 0,
          isHidden: Boolean(result.is_hidden),
        })),
      })
    } catch (err) {
      if (handleUnauthorized(err)) return

      const detail = err.response?.data?.detail ||
        'Backend is unavailable. Start the FastAPI server and try again.'
      setBackendOnline(Boolean(err.response))
      setRunResult({ success: false, output: detail, execTime: 'unavailable' })
    } finally {
      setIsRunning(false)
    }
  }, [authHeaders, handleUnauthorized])

  const submitForAnalysis = useCallback(async (code, language, problemId = null, problemDesc = null, onComplete) => {
    setIsAnalyzing(true)
    setAnalysisResult(null)

    try {
      const { data } = await axios.post(`${API_BASE}/submit`, {
        code,
        language,
        test_input: '',
        problem_id: problemId,
        problem_desc: problemDesc,
      }, {
        headers: authHeaders(),
        timeout: 30000,
      })

      setBackendOnline(true)
      const result = transformSubmissionResponse(data)
      setAnalysisResult(result)

      const firstTest = (data.failure_report?.test_results || [])[0]
      if (firstTest) {
        setRunResult({
          success: firstTest.status === 'PASSED',
          output: firstTest.actual_output || firstTest.error_message || '(no output)',
          execTime: `${firstTest.execution_time_ms || 0}ms`,
        })
      }

      if (onComplete) onComplete(result)
    } catch (err) {
      if (handleUnauthorized(err)) return

      const detail = err.response?.data?.detail ||
        'Backend is unavailable. Official tests were not run.'
      const result = buildOfflineResult(detail)
      setBackendOnline(Boolean(err.response))
      setAnalysisResult(result)
      setRunResult({ success: false, output: detail, execTime: 'unavailable' })
      if (onComplete) onComplete(result)
    } finally {
      setIsAnalyzing(false)
    }
  }, [authHeaders, handleUnauthorized])

  const reset = useCallback(() => {
    setAnalysisResult(null)
    setRunResult(null)
  }, [])

  const revealHint = useCallback(async (submissionId, userId = null) => {
    if (!submissionId) return null
    try {
      const { data } = await axios.post(`${API_BASE}/hint`, {
        submission_id: submissionId,
        user_id: userId,
      }, {
        headers: authHeaders(),
      })
      return data
    } catch (err) {
      console.error('[DebugMentor] /hint error:', err)
      return null
    }
  }, [authHeaders])

  const fetchProfile = useCallback(async (userId) => {
    try {
      const { data } = await axios.get(`${API_BASE}/profile/${userId}`, {
        headers: authHeaders(),
        timeout: 10000,
      })
      return data
    } catch (err) {
      console.error('[DebugMentor] /profile error:', err)
      return null
    }
  }, [authHeaders])

  const fetchPatterns = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/patterns`, {
        headers: authHeaders(),
        timeout: 10000,
      })
      return data?.patterns || []
    } catch (err) {
      console.error('[DebugMentor] /patterns error:', err)
      return []
    }
  }, [authHeaders])

  const fetchPatternProblems = useCallback(async (patternId) => {
    try {
      const { data } = await axios.get(`${API_BASE}/patterns/${patternId}/problems`, {
        headers: authHeaders(),
        timeout: 10000,
      })
      return data?.problems || []
    } catch (err) {
      console.error('[DebugMentor] /patterns/{id}/problems error:', err)
      return []
    }
  }, [authHeaders])

  const fetchProblemDetail = useCallback(async (problemId) => {
    try {
      const { data } = await axios.get(`${API_BASE}/problems/${problemId}`, {
        headers: authHeaders(),
        timeout: 10000,
      })
      return data
    } catch (err) {
      console.error('[DebugMentor] /problems/{id} error:', err)
      return null
    }
  }, [authHeaders])

  return {
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
  }
}
