export default function HintsTab({ submission, hints, busy, error, onRequestHint }) {
  if (!submission) {
    return (
      <div className="panel-empty">
        <strong>No submission selected</strong>
        <span>Submit a solution before requesting personalized guidance.</span>
      </div>
    )
  }

  if (submission.success) {
    return (
      <div className="panel-empty success-empty">
        <strong>No hint needed</strong>
        <span>This submission passed every official test.</span>
      </div>
    )
  }

  const highestLevel = hints.reduce((highest, hint) => Math.max(highest, hint.level), 0)
  const nextLabel = highestLevel === 0 ? 'Get hint 1' : highestLevel === 1 ? 'Get hint 2' : 'Reveal solution'

  return (
    <div className="hints-view">
      <header className="hints-header">
        <div>
          <strong>Personalized guidance</strong>
          <p>Hints are generated from this submission and its test results.</p>
        </div>
        {submission.hintsAvailable && highestLevel < 3 && (
          <button className="button button-primary" disabled={busy} type="button" onClick={onRequestHint}>
            {busy ? 'Generating' : nextLabel}
          </button>
        )}
      </header>

      {!submission.hintsAvailable && (
        <div className="panel-message">
          AI hints are not configured on the backend. Add a Gemini API key to enable them.
        </div>
      )}
      {error && <div className="panel-message panel-message-error">{error}</div>}

      {hints.length === 0 && submission.hintsAvailable && !error && (
        <div className="hint-ready-state">
          <span>Level 1</span>
          <strong>Start with a focused nudge</strong>
        </div>
      )}

      <div className="hint-list">
        {hints.map((hint) => (
          <article className={`hint-item ${hint.isSolution ? 'solution-hint' : ''}`} key={hint.level}>
            <header>
              <span>{hint.isSolution ? 'Solution' : `Hint ${hint.level}`}</span>
              <small>{hint.focus}</small>
            </header>
            <h3>{hint.title}</h3>
            <p>{hint.content}</p>
            {hint.solutionCode && <pre className="solution-code"><code>{hint.solutionCode}</code></pre>}
          </article>
        ))}
      </div>
    </div>
  )
}
