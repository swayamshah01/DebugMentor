import HintCard from './HintCard'
import SolutionModal from './SolutionModal'

export function HintsTab({
  analysisResult,
  isAnalyzing,
  revealedHints,
  showSolutionModal,
  onNextHint,
  onShowSolutionModal,
  onCancelModal,
  onRevealSolution,
}) {
  if (isAnalyzing) {
    return (
      <div className="fade-in">
        <div className="skeleton" style={{ height: 80, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 100, marginBottom: 10 }} />
        <div className="skeleton" style={{ height: 100, marginBottom: 10, opacity: 0.6 }} />
        <div className="skeleton" style={{ height: 100, opacity: 0.3 }} />
      </div>
    )
  }

  if (!analysisResult) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🧠</div>
        <div className="empty-title">No analysis yet</div>
        <div className="empty-desc">
          Submit your code for AI analysis to receive progressive hints.
        </div>
      </div>
    )
  }

  const { hints, bugSummary, testCases, status } = analysisResult
  const isClean = status === 'clean'
  const passed = testCases.filter(t => t.passed).length
  const failed = testCases.filter(t => !t.passed).length

  return (
    <div className="fade-in">
      {/* Analysis Summary — adapts based on scenario */}
      <div className="analysis-summary-card" style={isClean ? {
        borderColor: 'rgba(79, 255, 176, 0.25)',
        background: 'rgba(79, 255, 176, 0.04)'
      } : {}}>
        <div className="analysis-summary-label">● Analysis Summary</div>
        <p className="analysis-summary-text">
          {isClean ? (
            <>
              <span className="highlight green">✓ No bugs detected</span> — all{' '}
              <span className="highlight green">{passed} of {testCases.length} test cases pass.</span>
              {' '}Here are some tips to improve your code further.
            </>
          ) : (
            <>
              Found{' '}
              <span className="highlight">
                {failed} {failed === 1 ? 'bug' : 'bugs'}
              </span>
              {' '}— {bugSummary}.{' '}
              <span className="highlight green">{passed} of {testCases.length} test cases pass.</span>
            </>
          )}
        </p>
        <div className="test-chips">
          {testCases.map(tc => (
            <div key={tc.id} className={`test-chip ${tc.passed ? 'pass' : 'fail'}`}>
              {tc.passed ? '✓' : '✗'} {tc.input}
            </div>
          ))}
        </div>
      </div>

      {/* Hint Cards */}
      {hints.map(hint => (
        <HintCard
          key={hint.level}
          hint={hint}
          revealed={revealedHints >= hint.level}
          isClean={isClean}
        />
      ))}

      {/* Next hint button — only shown for buggy code */}
      {!isClean && revealedHints < 2 && (
        <button
          id="btn-next-hint"
          className="btn-next-hint"
          onClick={onNextHint}
        >
          <span>🤔</span>
          I'm still stuck → Show next hint
          <span style={{ marginLeft: 'auto', fontSize: 11, opacity: 0.7 }}>
            H{revealedHints + 1} of 3
          </span>
        </button>
      )}

      {!isClean && revealedHints === 2 && (
        <button
          id="btn-show-solution"
          className="btn-next-hint"
          style={{
            borderColor: 'rgba(255, 95, 109, 0.3)',
            background: 'rgba(255, 95, 109, 0.06)',
            color: 'var(--accent-danger)'
          }}
          onClick={onShowSolutionModal}
        >
          <span>🔓</span>
          Show Full Solution
          <span style={{ marginLeft: 'auto', fontSize: 11, opacity: 0.7 }}>Logged</span>
        </button>
      )}

      {/* Footer meta */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        marginTop: 16,
        fontFamily: 'var(--font-body)',
        fontSize: 12,
        color: 'var(--text-secondary)'
      }}>
        <span>{isClean ? 'Tips:' : 'Hints:'}</span>
        <span style={{ color: isClean ? 'var(--accent-primary)' : 'var(--accent-secondary)', fontWeight: 600 }}>
          {revealedHints}/3
        </span>
        <span style={{ marginLeft: 'auto' }}>Attempts: 2</span>
        <span>·</span>
        <span>Last saved 2m ago</span>
      </div>

      {/* Solution Modal */}
      {showSolutionModal && (
        <SolutionModal onCancel={onCancelModal} onReveal={onRevealSolution} />
      )}
    </div>
  )
}
