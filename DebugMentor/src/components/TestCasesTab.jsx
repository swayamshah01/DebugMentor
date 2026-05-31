export function TestCasesTab({
  problem,
  analysisResult,
  runResult,
  isAnalyzing,
  selectedVisibleTestCaseId,
  onSelectVisibleTestCase,
}) {
  if (isAnalyzing) {
    return (
      <div className="fade-in">
        <div className="skeleton" style={{ height: 40, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 200 }} />
      </div>
    )
  }

  if (!analysisResult) {
    const visibleTests = problem?.test_cases || []
    const practiceResults = runResult?.testCases || []
    const practiceByLabel = new Map(practiceResults.map((item) => [item.label, item]))
    const passedVisible = practiceResults.filter((item) => item.passed).length
    const failedVisible = practiceResults.filter((item) => !item.passed).length

    return (
      <div className="fade-in">
        {practiceResults.length > 0 && (
          <div className="test-header">
            <div className="test-count-badge">
              <span className="tc-badge">Visible Tests</span>
              <span className="tc-badge pass">{passedVisible} Passed</span>
              <span className="tc-badge fail">{failedVisible} Failed</span>
            </div>

            {runResult?.dominantFailureType && (
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
                {runResult.dominantFailureType.replaceAll('_', ' ')}
              </div>
            )}
          </div>
        )}

        <div className="testcase-tabs">
          {visibleTests.map((testCase, index) => (
            <button
              key={testCase.id}
              type="button"
              className={`testcase-tab ${selectedVisibleTestCaseId === testCase.id ? 'active' : ''}`}
              onClick={() => onSelectVisibleTestCase && onSelectVisibleTestCase(testCase)}
            >
              Case {index + 1}
            </button>
          ))}
        </div>

        {visibleTests.length > 0 ? (
          <div className="leetcode-case-list">
            {visibleTests.map((testCase, index) => {
              const practice = practiceByLabel.get(testCase.label)
              return (
              <button
                key={testCase.id}
                type="button"
                className={`leetcode-case-card ${selectedVisibleTestCaseId === testCase.id ? 'active' : ''} ${practice ? (practice.passed ? 'passed' : 'failed') : ''}`}
                onClick={() => onSelectVisibleTestCase && onSelectVisibleTestCase(testCase)}
              >
                <div className="case-card-title">Case {index + 1}</div>
                <div className="case-field">
                  <div className="case-label">Input</div>
                  <pre>{testCase.input}</pre>
                </div>
                <div className="case-field">
                  <div className="case-label">Expected</div>
                  <pre>{testCase.expected_output}</pre>
                </div>
                {practice && (
                  <div className="case-field">
                    <div className="case-label">Actual</div>
                    <pre>{practice.actual}</pre>
                  </div>
                )}
                {practice && (
                  <div className="case-field">
                    <div className="case-label">Status</div>
                    <pre>{practice.passed ? 'Passed' : (practice.status || 'Failed')}</pre>
                  </div>
                )}
              </button>
              )
            })}
          </div>
        ) : (
          <div className="empty-state compact">
            <div className="empty-title">No sample cases</div>
            <div className="empty-desc">Choose a problem with visible tests.</div>
          </div>
        )}

        {practiceResults.length > 0 && (
          <div
            style={{
              marginTop: 16,
              padding: '10px 14px',
              background: failedVisible > 0 ? 'rgba(220, 53, 69, 0.05)' : 'rgba(40, 167, 69, 0.06)',
              border: `1px solid ${failedVisible > 0 ? 'rgba(220, 53, 69, 0.14)' : 'rgba(40, 167, 69, 0.14)'}`,
              borderRadius: 6,
              fontFamily: 'var(--font-body)',
              fontSize: 13,
              color: 'var(--text-secondary)',
            }}
          >
            {runResult.output}
          </div>
        )}
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
