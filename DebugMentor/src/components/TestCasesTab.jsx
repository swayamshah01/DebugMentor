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
        <div className="empty-title">No official results yet</div>
        <div className="empty-desc">
          Submit the current problem to run the official visible and hidden cases.
        </div>
      </div>
    )
  }

  const { testCases = [], failureReport } = analysisResult
  const passed = testCases.filter((testCase) => testCase.passed).length
  const failed = testCases.filter((testCase) => !testCase.passed).length
  const hiddenCount = testCases.filter((testCase) => testCase.isHidden).length

  return (
    <div className="fade-in">
      <div className="test-header">
        <div className="test-count-badge">
          <span className="tc-badge">{testCases.length} Official Tests</span>
          <span className="tc-badge pass">{passed} Passed</span>
          <span className="tc-badge fail">{failed} Failed</span>
          {hiddenCount > 0 && <span className="tc-badge">{hiddenCount} Hidden</span>}
        </div>

        {failureReport?.dominant_failure_type && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '4px 10px',
              background: 'rgba(220, 53, 69, 0.08)',
              border: '1px solid rgba(220, 53, 69, 0.18)',
              borderRadius: 4,
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
              color: 'var(--accent-danger)',
            }}
          >
            {failureReport.dominant_failure_type.replaceAll('_', ' ')}
          </div>
        )}
      </div>

      <table className="test-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Input</th>
            <th>Label</th>
            <th>Expected / Actual</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {testCases.map((testCase, index) => (
            <tr
              key={`${testCase.id}-${index}`}
              className={`test-row ${testCase.passed ? 'pass' : 'fail'}`}
              id={`test-row-${testCase.id}`}
            >
              <td style={{ color: 'var(--text-secondary)', width: 36 }}>
                {testCase.isHidden ? 'H' : index + 1}
              </td>
              <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                {testCase.isHidden ? 'Hidden input' : testCase.input}
              </td>
              <td style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
                {testCase.label}
                {testCase.isHidden ? ' (Hidden)' : ''}
              </td>
              <td
                style={{
                  color: testCase.passed ? 'var(--accent-primary)' : 'var(--accent-danger)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 12,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {testCase.isHidden ? (
                  <div>Official hidden check</div>
                ) : (
                  <>
                    <div style={{ color: 'var(--text-secondary)', fontSize: 11 }}>
                      Exp: {testCase.expected}
                    </div>
                    <div style={{ marginTop: 4 }}>
                      Act: {testCase.actual}
                    </div>
                  </>
                )}
              </td>
              <td>
                <span className={`status-pill ${testCase.passed ? 'pass' : 'fail'}`}>
                  {testCase.passed ? 'Pass' : (testCase.status || 'Fail')}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div
        style={{
          marginTop: 16,
          padding: '10px 14px',
          background: failed > 0 ? 'rgba(220, 53, 69, 0.05)' : 'rgba(40, 167, 69, 0.06)',
          border: `1px solid ${failed > 0 ? 'rgba(220, 53, 69, 0.14)' : 'rgba(40, 167, 69, 0.14)'}`,
          borderRadius: 6,
          fontFamily: 'var(--font-body)',
          fontSize: 13,
          color: 'var(--text-secondary)',
        }}
      >
        {failureReport?.failure_summary ||
          (failed > 0
            ? `${failed} test case${failed > 1 ? 's' : ''} failed.`
            : `All ${passed} test cases passed successfully.`)}
      </div>
    </div>
  )
}
