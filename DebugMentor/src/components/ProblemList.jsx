export default function ProblemList({ problems = [], selectedProblemId, onSelectProblem }) {
  return (
    <section className="problem-browser">
      <div className="sidebar-section-title">Problems</div>
      <div className="problem-list">
        {problems.map((problem) => {
          const active = problem.id === selectedProblemId
          return (
            <button
              key={problem.id}
              className={`problem-item ${active ? 'active' : ''}`}
              onClick={() => onSelectProblem(problem.id)}
            >
              <div className="problem-item-header">
                <div>
                  <div className="problem-title">{problem.title}</div>
                  <div className="problem-subtitle">{problem.short_description || ''}</div>
                </div>
                <span className={`difficulty difficulty-${problem.difficulty}`}>{problem.difficulty}</span>
              </div>
              <div className="problem-state-row">
                <span>Order {problem.order_index || 0}</span>
                {problem.solved_count !== undefined && <span>{problem.solved_count} solved</span>}
              </div>
            </button>
          )
        })}
      </div>
    </section>
  )
}
