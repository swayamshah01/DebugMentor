export default function ProblemStatement({ problem, loading, selectedVisibleTestCaseId, onSelectVisibleTestCase }) {
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
        </div>
        <span className={`difficulty difficulty-${problem.difficulty}`}>{problem.difficulty}</span>
      </div>

      <p className="problem-text">{problem.statement}</p>

      {problem.constraints && (
        <div className="info-block">
          <div className="info-label">Constraints</div>
          <div className="info-text">{problem.constraints}</div>
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

      {Array.isArray(problem.test_cases) && problem.test_cases.length > 0 && (
        <div className="examples-block">
          <div className="info-label">Visible tests</div>
          {problem.test_cases.map((testCase) => (
            <button
              key={testCase.id}
              type="button"
              className={`example-card example-card-button ${selectedVisibleTestCaseId === testCase.id ? 'active' : ''}`}
              onClick={() => onSelectVisibleTestCase && onSelectVisibleTestCase(testCase)}
            >
              <div><strong>{testCase.label}</strong></div>
              <div><strong>Input:</strong> {testCase.input}</div>
              <div><strong>Expected:</strong> {testCase.expected_output}</div>
            </button>
          ))}
        </div>
      )}
    </section>
  )
}
