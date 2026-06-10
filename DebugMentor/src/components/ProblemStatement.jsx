export default function ProblemStatement({ problem, loading }) {
  const constraintItems = problem?.constraints
    ? String(problem.constraints).split(',').map((item) => item.trim()).filter(Boolean)
    : []

  if (loading) {
    return (
      <section className="problem-statement-panel">
        <div className="skeleton" style={{ height: 24, width: '55%', marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 120, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 160 }} />
      </section>
    )
  }

  if (!problem) {
    return (
      <section className="problem-statement-panel empty-state-panel">
        <div className="empty-title">Select a problem</div>
        <div className="empty-desc">Choose a curated question from a pattern to open the practice workspace.</div>
      </section>
    )
  }

  return (
    <section className="problem-statement-panel">
      <div className="problem-header">
        <div>
          <div className="problem-kicker">{problem.pattern?.name || 'Pattern'}</div>
          <h2>{problem.title}</h2>
          {problem.short_description && (
            <p className="problem-subtitle" style={{ marginTop: 8 }}>
              {problem.short_description}
            </p>
          )}
        </div>
        <span className={`difficulty difficulty-${problem.difficulty}`}>{problem.difficulty}</span>
      </div>

      <div className="info-block">
        <div className="info-label">Problem</div>
        <p className="problem-text" style={{ marginBottom: 0 }}>{problem.statement}</p>
      </div>

      {constraintItems.length > 0 && (
        <div className="info-block">
          <div className="info-label">Constraints</div>
          <ul className="info-text" style={{ paddingLeft: 18 }}>
            {constraintItems.map((item, index) => (
              <li key={`${item}-${index}`} style={{ marginBottom: 6 }}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {Array.isArray(problem.examples) && problem.examples.length > 0 && (
        <div className="examples-block">
          <div className="info-label">Examples</div>
          {problem.examples.map((example, index) => (
            <div key={index} className="example-card">
              <div><strong>Input:</strong> {example.input}</div>
              <div><strong>Output:</strong> {example.output}</div>
              {example.explanation && <div><strong>Why:</strong> {example.explanation}</div>}
            </div>
          ))}
        </div>
      )}

    </section>
  )
}
