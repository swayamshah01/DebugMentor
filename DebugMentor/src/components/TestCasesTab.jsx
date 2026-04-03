// TestCasesTab.jsx
export function TestCasesTab({ analysisResult, isAnalyzing }) {
  if (isAnalyzing) {
    return (
      <div className="fade-in">
        <div className="skeleton" style={{ height: 40, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 200 }} />
      </div>
    )
  }

  if (!analysisResult) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🧪</div>
        <div className="empty-title">No test cases yet</div>
        <div className="empty-desc">
          Submit your code to generate and run test cases automatically.
        </div>
      </div>
    )
  }

  const { testCases } = analysisResult
  const passed = testCases.filter(t => t.passed).length
  const failed = testCases.filter(t => !t.passed).length

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="test-header">
        <div className="test-count-badge">
          <span className="tc-badge">{testCases.length} Tests</span>
          <span className="tc-badge pass">✓ {passed} Passed</span>
          <span className="tc-badge fail">✗ {failed} Failed</span>
        </div>
        <button id="btn-regenerate" className="btn-regenerate">
          🔄 Regenerate
        </button>
      </div>

      {/* Table */}
      <table className="test-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Input</th>
            <th>Expected</th>
            <th>Your Output</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {testCases.map(tc => (
            <tr
              key={tc.id}
              className={`test-row ${tc.passed ? 'pass' : 'fail'}`}
              id={`test-row-${tc.id}`}
            >
              <td style={{ color: 'var(--text-secondary)', width: 30 }}>{tc.id}</td>
              <td>{tc.input}</td>
              <td style={{ color: 'var(--accent-primary)' }}>{tc.expected}</td>
              <td style={{ color: tc.passed ? 'var(--text-primary)' : 'var(--accent-danger)' }}>
                {tc.actual}
              </td>
              <td>
                <span className={`status-pill ${tc.passed ? 'pass' : 'fail'}`}>
                  {tc.passed ? '✅' : '❌'} {tc.passed ? 'Pass' : 'Fail'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Test summary note — dynamic per scenario */}
      <div style={{
        marginTop: 16,
        padding: '10px 14px',
        background: failed > 0 ? 'rgba(255, 95, 109, 0.05)' : 'rgba(79, 255, 176, 0.05)',
        border: `1px solid ${failed > 0 ? 'rgba(255, 95, 109, 0.15)' : 'rgba(79, 255, 176, 0.15)'}`,
        borderRadius: 6,
        fontFamily: 'var(--font-body)',
        fontSize: 13,
        color: 'var(--text-secondary)',
        display: 'flex',
        alignItems: 'center',
        gap: 8
      }}>
        <span>{failed > 0 ? '❌' : '✅'}</span>
        <span>
          {failed > 0
            ? `${failed} test case${failed > 1 ? 's' : ''} failed — ${analysisResult.bugSummary}.`
            : `All ${passed} test cases passed successfully.`
          }
        </span>
      </div>
    </div>
  )
}
