function Difficulty({ value }) {
  return <span className={`difficulty difficulty-${value}`}>{value}</span>
}


export default function PatternExplorerPage({
  patterns,
  loading,
  expandedPatternId,
  problemsByPattern,
  loadingPatternId,
  profile,
  onTogglePattern,
  onSelectProblem,
}) {
  const stats = profile?.stats

  return (
    <main className="explorer-page">
      <header className="page-heading explorer-heading">
        <div>
          <span className="eyebrow">Practice library</span>
          <h1>Choose a pattern</h1>
          <p>Open a topic, select a question, and work through one case at a time.</p>
        </div>
        <div className="progress-summary" aria-label="Practice progress">
          <div><strong>{profile?.solved_problems_count ?? 0}</strong><span>Solved</span></div>
          <div><strong>{stats ? `${Math.round(stats.pass_rate)}%` : '-'}</strong><span>Pass rate</span></div>
          <div><strong>{profile?.readiness_snapshot?.recent_streak ?? 0}</strong><span>Day streak</span></div>
        </div>
      </header>

      {loading ? (
        <div className="page-state">Loading practice library...</div>
      ) : patterns.length === 0 ? (
        <div className="page-state error-state">
          <strong>No questions are available.</strong>
          <span>Check that the backend migrations and curated content sync completed.</span>
        </div>
      ) : (
        <section className="pattern-list" aria-label="DSA patterns">
          {patterns.map((pattern) => {
            const expanded = expandedPatternId === pattern.id
            const problems = problemsByPattern[pattern.id] || []
            return (
              <div className={`pattern-section ${expanded ? 'expanded' : ''}`} key={pattern.id}>
                <button
                  className="pattern-trigger"
                  type="button"
                  aria-expanded={expanded}
                  onClick={() => onTogglePattern(pattern.id)}
                >
                  <span className="pattern-code">{pattern.icon_name || pattern.name.slice(0, 2)}</span>
                  <span className="pattern-copy">
                    <strong>{pattern.name}</strong>
                    <small>{pattern.description}</small>
                  </span>
                  <span className="pattern-count">{pattern.problem_count} questions</span>
                  <span className="pattern-toggle" aria-hidden="true">{expanded ? '-' : '+'}</span>
                </button>

                {expanded && (
                  <div className="problem-list">
                    {loadingPatternId === pattern.id ? (
                      <div className="inline-state">Loading questions...</div>
                    ) : problems.length === 0 ? (
                      <div className="inline-state">No active questions in this pattern.</div>
                    ) : problems.map((problem, index) => (
                      <button
                        className="problem-row"
                        type="button"
                        key={problem.id}
                        onClick={() => onSelectProblem(problem.id)}
                      >
                        <span className="problem-number">{String(index + 1).padStart(2, '0')}</span>
                        <span className="problem-row-copy">
                          <strong>{problem.title}</strong>
                          <small>{problem.short_description}</small>
                        </span>
                        <Difficulty value={problem.difficulty} />
                        <span className="open-label">Open</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </section>
      )}
    </main>
  )
}
