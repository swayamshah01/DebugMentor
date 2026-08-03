import { useCallback, useState } from 'react'
import axios from 'axios'


const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'


function errorMessage(error, fallback) {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(' ')
  return fallback
}


function mapGrade(data) {
  if (!data) return null
  return {
    success: data.success,
    mode: data.mode,
    summary: data.summary,
    totalTests: data.total_tests,
    passedTests: data.passed_tests,
    failedTests: data.failed_tests,
    failureType: data.dominant_failure_type,
    submissionId: data.submission_id || null,
    problemId: data.problem_id || null,
    status: data.status || (data.success ? 'passed' : 'failed'),
    hintsAvailable: Boolean(data.hints_available),
    submittedAt: data.submitted_at || null,
    testResults: (data.test_results || []).map((result) => ({
      id: result.test_case_id,
      label: result.label,
      input: result.input,
      expected: result.expected_output,
      actual: result.actual_output,
      error: result.error_summary,
      executionTimeMs: result.execution_time_ms,
      stage: result.stage,
      hidden: result.is_hidden,
      status: result.status,
      passed: result.status === 'PASSED',
    })),
  }
}


export function usePractice(token, onUnauthorized) {
  const [busyAction, setBusyAction] = useState(null)
  const [gradeResult, setGradeResult] = useState(null)
  const [submissionResult, setSubmissionResult] = useState(null)
  const [hints, setHints] = useState([])
  const [requestError, setRequestError] = useState('')
  const [hintError, setHintError] = useState('')

  const headers = useCallback(() => ({ Authorization: `Bearer ${token}` }), [token])

  const handleError = useCallback((error, fallback) => {
    if (error.response?.status === 401) onUnauthorized?.()
    return errorMessage(error, fallback)
  }, [onUnauthorized])

  const runSolution = useCallback(async ({ code, language, problemId, testCaseId }) => {
    setBusyAction('run')
    setRequestError('')
    try {
      const { data } = await axios.post(`${API_BASE}/run`, {
        code,
        language,
        problem_id: problemId,
        test_case_id: testCaseId,
      }, { headers: headers(), timeout: 20000 })
      const result = mapGrade(data)
      setGradeResult(result)
      return result
    } catch (error) {
      setRequestError(handleError(error, 'The selected test could not be run.'))
      return null
    } finally {
      setBusyAction(null)
    }
  }, [handleError, headers])

  const submitSolution = useCallback(async ({ code, language, problemId }) => {
    setBusyAction('submit')
    setRequestError('')
    setHintError('')
    setHints([])
    try {
      const { data } = await axios.post(`${API_BASE}/submit`, {
        code,
        language,
        problem_id: problemId,
      }, { headers: headers(), timeout: 45000 })
      const result = mapGrade(data)
      setGradeResult(result)
      setSubmissionResult(result)
      return result
    } catch (error) {
      setRequestError(handleError(error, 'The official submission could not be graded.'))
      return null
    } finally {
      setBusyAction(null)
    }
  }, [handleError, headers])

  const requestNextHint = useCallback(async () => {
    if (!submissionResult?.submissionId) return null
    setBusyAction('hint')
    setHintError('')
    try {
      const { data } = await axios.post(`${API_BASE}/hint`, {
        submission_id: submissionResult.submissionId,
      }, { headers: headers(), timeout: 45000 })
      const hint = {
        level: data.level,
        title: data.title,
        content: data.content,
        focus: data.focus,
        isSolution: data.is_solution,
        solutionCode: data.solution_code,
        levelsRemaining: data.levels_remaining,
      }
      setHints((current) => [...current.filter((item) => item.level !== hint.level), hint].sort((a, b) => a.level - b.level))
      return hint
    } catch (error) {
      setHintError(handleError(error, 'A personalized hint could not be generated.'))
      return null
    } finally {
      setBusyAction(null)
    }
  }, [handleError, headers, submissionResult])

  const resetPractice = useCallback(() => {
    setGradeResult(null)
    setSubmissionResult(null)
    setHints([])
    setRequestError('')
    setHintError('')
  }, [])

  const get = useCallback(async (path, fallback) => {
    try {
      const { data } = await axios.get(`${API_BASE}${path}`, { headers: headers(), timeout: 12000 })
      return data
    } catch (error) {
      setRequestError(handleError(error, fallback))
      return null
    }
  }, [handleError, headers])

  return {
    busyAction,
    gradeResult,
    submissionResult,
    hints,
    requestError,
    hintError,
    runSolution,
    submitSolution,
    requestNextHint,
    resetPractice,
    fetchPatterns: useCallback(async () => (await get('/patterns', 'Patterns could not be loaded.'))?.patterns || [], [get]),
    fetchPatternProblems: useCallback(async (patternId) => (await get(`/patterns/${patternId}/problems`, 'Questions could not be loaded.'))?.problems || [], [get]),
    fetchProblem: useCallback((problemId) => get(`/problems/${problemId}`, 'The problem could not be loaded.'), [get]),
    fetchProfile: useCallback((userId) => get(`/profile/${userId}`, 'The profile could not be loaded.'), [get]),
  }
}
