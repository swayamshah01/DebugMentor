export default function PatternExplorerPage({
  patterns = [],
  loading = false,
  expandedPatternId = null,
  patternProblemsById = {},
  loadingPatternId = null,
  onTogglePattern,
  onSelectProblem,
}) {
  return (
    <main className="pattern-explorer-page">
      <header className="pattern-explorer-header">
        <div>
          <div className="explorer-kicker">Pattern Explorer</div>
          <h1>Choose a DSA pattern to practice</h1>
          <p>Expand a pattern, then pick a curated problem to open the workspace.</p>
        </div>
      </header>

      <section className="pattern-explorer-list">
        {patterns.map((pattern) => {
          const isOpen = pattern.id === expandedPatternId
          const problems = patternProblemsById[pattern.id] || []
          const isLoadingQuestions = loadingPatternId === pattern.id

          return (
            <article key={pattern.id} className={`pattern-explorer-card ${isOpen ? 'active' : ''}`}>
              <button
                type="button"
                className="pattern-explorer-row"
                onClick={() => onTogglePattern(pattern.id)}
              >
                <div className="pattern-explorer-main">
                  <span className="pattern-explorer-icon">{pattern.icon_name || pattern.icon || '[]'}</span>
                  <div>
                    <div className="pattern-explorer-title">{pattern.name}</div>
                    <div className="pattern-explorer-desc">{pattern.description || 'Curated practice set'}</div>
                  </div>
                </div>
                <div className="pattern-explorer-meta">
                  <span>{pattern.problem_count || 0} questions</span>
                  <span className={`pattern-chevron ${isOpen ? 'open' : ''}`}>v</span>
                </div>
              </button>

              {isOpen && (
                <div className="pattern-question-list">
                  {isLoadingQuestions ? (
                    <div className="pattern-question-loading">Loading questions...</div>
                  ) : problems.length > 0 ? (
                    problems.map((problem) => (
                      <button
                        key={problem.id}
                        type="button"
                        className="pattern-question-row"
                        onClick={() => onSelectProblem(problem.id)}
                      >
                        <div>
                          <div className="pattern-question-title">{problem.title}</div>
                          <div className="pattern-question-subtitle">{problem.short_description || 'Curated interview question'}</div>
                        </div>
                        <div className="pattern-question-right">
                          <span className={`difficulty difficulty-${problem.difficulty}`}>{problem.difficulty}</span>
                          <span className="pattern-question-order">#{problem.order_index || 0}</span>
                        </div>
                      </button>
                    ))
                  ) : (
                    <div className="pattern-question-loading">No questions found for this pattern.</div>
                  )}
                </div>
              )}
            </article>
          )
        })}
      </section>

      {!loading && patterns.length === 0 && (
        <div className="pattern-explorer-empty">
          No patterns are available yet.
        </div>
      )}
    </main>
  )
}
