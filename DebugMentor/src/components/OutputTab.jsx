// OutputTab.jsx
export function OutputTab({ runResult, isRunning }) {
  if (isRunning) {
    return (
      <div className="fade-in">
        <div className="skeleton" style={{ height: 120, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 60 }} />
      </div>
    )
  }

  if (!runResult) {
    return (
      <div className="empty-state">
        <div className="empty-icon">▶</div>
        <div className="empty-title">No output yet</div>
        <div className="empty-desc">Click "Run Code" to see the execution output here.</div>
      </div>
    )
  }

  return (
    <div className="fade-in">
      <div className="terminal-block">
        <div className="terminal-header">
          <span className="term-dot red" />
          <span className="term-dot yellow" />
          <span className="term-dot green" />
          <span className="term-label">python solution.py</span>
        </div>
        <div className="terminal-output">
          {runResult.success ? (
            <>
              <span className="muted">{'>>> '}[Output] </span>
              <span className="success-text">{runResult.output}</span>
              {'\n'}
              <span className="muted">Execution time: {runResult.execTime}</span>
            </>
          ) : (
            <>
              <span className="error-text">{runResult.output}</span>
              {'\n'}
              <span className="muted">Execution time: {runResult.execTime}</span>
            </>
          )}
        </div>
      </div>

      <div className={`output-status-card ${runResult.success ? 'success' : 'error'}`}>
        <span className="status-icon">{runResult.success ? '✅' : '❌'}</span>
        <div>
          <div className={`status-label ${runResult.success ? 'success-text' : 'error-text'}`}>
            {runResult.success ? 'Ran successfully' : 'Runtime Error'}
          </div>
          {!runResult.success && (
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', fontFamily: 'var(--font-body)', marginTop: 2 }}>
              {runResult.output.split('\n')[0]}
            </div>
          )}
        </div>
        <div className="exec-time">
          Execution time: {runResult.execTime}
        </div>
      </div>
    </div>
  )
}
