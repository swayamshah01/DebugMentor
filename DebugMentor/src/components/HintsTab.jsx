import { useEffect, useState } from 'react'
import HintCard from './HintCard'
import SolutionModal from './SolutionModal'

export function HintsTab({ analysisResult, isAnalyzing, revealHint }) {
  const [revealedLevel, setRevealedLevel] = useState(1)
  const [isRevealing, setIsRevealing] = useState(false)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    if (analysisResult?.submissionId) {
      setRevealedLevel(1)
      setShowModal(false)
    }
  }, [analysisResult?.submissionId])

  if (isAnalyzing) {
    return (
      <div className="fade-in">
        <div className="skeleton" style={{ height: 80, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 100, marginBottom: 10 }} />
        <div className="skeleton" style={{ height: 100, marginBottom: 10, opacity: 0.6 }} />
      </div>
    )
  }

  if (!analysisResult) {
    return (
      <div className="empty-state compact">
        <div className="empty-title">No hints yet</div>
        <div className="empty-desc">Submit your code to generate feedback and progressive hints.</div>
      </div>
    )
  }

  const { hints, status, bugSummary } = analysisResult
  const isClean = status === 'clean'

  const normHints = Array.isArray(hints)
    ? {
        explanation: bugSummary || 'Review the failed cases and compare your output with the expected result.',
        hint_1: hints[0]?.text || '',
        hint_2: hints[1]?.text || '',
        hint_3: hints[2]?.text || '',
      }
    : (hints || {})

  const solutionText = normHints.solution_code || normHints.hint_3 || 'No reference solution is available for this submission.'

  if (isClean) {
    return (
      <div className="fade-in">
        <div className="analysis-summary-card success">
          <div className="analysis-summary-label">Feedback</div>
          <p className="analysis-summary-text">
            <span className="highlight green">All checks passed.</span> Your current solution matches the official tests.
          </p>
        </div>
      </div>
    )
  }

  const handleReveal = async () => {
    if (revealedLevel >= 3) return
    if (revealedLevel === 2) {
      setShowModal(true)
      return
    }

    setIsRevealing(true)
    await revealHint(analysisResult.submissionId, null)
    setRevealedLevel(2)
    setIsRevealing(false)
  }

  const confirmSolution = async () => {
    setIsRevealing(true)
    setShowModal(false)
    await revealHint(analysisResult.submissionId, null)
    setRevealedLevel(3)
    setIsRevealing(false)
  }

  return (
    <div className="fade-in hints-layout">
      <div className="analysis-summary-card">
        <div className="analysis-summary-label">Feedback</div>
        <p className="analysis-summary-text">
          {normHints.explanation || bugSummary || 'Your submission did not pass all checks.'}
        </p>
      </div>

      <HintCard
        hint={{ level: 1, title: 'First Hint', text: normHints.hint_1 }}
        revealed={revealedLevel >= 1}
      />
      <HintCard
        hint={{ level: 2, title: 'Deeper Hint', text: normHints.hint_2 }}
        revealed={revealedLevel >= 2}
      />
      <HintCard
        hint={{ level: 3, title: 'Reference Solution', text: solutionText }}
        revealed={revealedLevel >= 3}
      />

      {revealedLevel < 3 && (
        <button
          type="button"
          onClick={handleReveal}
          disabled={isRevealing}
          className="btn-next-hint"
        >
          {isRevealing ? 'Loading...' : (revealedLevel === 2 ? 'Show Solution' : 'Get Next Hint')}
        </button>
      )}

      {showModal && (
        <SolutionModal
          onCancel={() => setShowModal(false)}
          onReveal={confirmSolution}
        />
      )}
    </div>
  )
}
