export default function PatternSidebar({ patterns = [], selectedPatternId, onSelectPattern, profileSummary }) {
  return (
    <aside className="pattern-sidebar">
      <div className="sidebar-section-title">Patterns</div>
      <div className="pattern-list">
        {patterns.map((pattern) => {
          const active = pattern.id === selectedPatternId
          return (
            <button
              key={pattern.id}
              className={`pattern-item ${active ? 'active' : ''}`}
              onClick={() => onSelectPattern(pattern.id)}
            >
              <div className="pattern-item-top">
                <span className="pattern-icon">{pattern.icon_name || pattern.icon || '◆'}</span>
                <span className="pattern-name">{pattern.name}</span>
              </div>
              <div className="pattern-meta">
                <span>{pattern.problem_count || 0} questions</span>
                {profileSummary?.[pattern.id] && (
                  <span>{profileSummary[pattern.id].mastery_percent.toFixed(0)}%</span>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </aside>
  )
}
