import { useState } from 'react'


function statusLabel(status) {
  return String(status || 'FAILED').replaceAll('_', ' ').toLowerCase()
}


function caseLabel(item, index, problem) {
  if (item.hidden) return `Hidden ${index + 1}`
  const visibleIndex = (problem?.test_cases || []).findIndex((testCase) => testCase.id === item.id)
  return `Case ${visibleIndex >= 0 ? visibleIndex + 1 : index + 1}`
}


export default function ResultPanel({ result, requestError, problem }) {
  const [selectedTestId, setSelectedTestId] = useState(null)

  if (requestError) {
    return <div className="panel-message panel-message-error">{requestError}</div>
  }

  if (!result) {
    return (
      <div className="panel-empty">
        <strong>No result yet</strong>
        <span>Run the selected case or submit your solution.</span>
      </div>
    )
  }

  const selectedIndex = Math.max(0, result.testResults.findIndex((item) => item.id === selectedTestId))
  const test = result.testResults[selectedIndex] || result.testResults[0]

  return (
    <div className="result-view">
      <header className={`result-summary ${result.success ? 'success' : 'failure'}`}>
        <div>
          <strong>{result.success ? 'Accepted' : statusLabel(result.failureType || 'Not accepted')}</strong>
          <p>{result.summary}</p>
        </div>
        <div className="result-count">
          <strong>{result.passedTests}/{result.totalTests}</strong>
          <span>passed</span>
        </div>
      </header>

      {result.testResults.length > 0 && (
        <>
          <div className="result-tabs" role="tablist" aria-label="Graded test cases">
            {result.testResults.map((item, index) => (
              <button
                type="button"
                role="tab"
                aria-selected={index === selectedIndex}
                className={`${index === selectedIndex ? 'active' : ''} ${item.passed ? 'passed' : 'failed'}`}
                key={`${item.id}-${index}`}
                onClick={() => setSelectedTestId(item.id)}
              >
                {caseLabel(item, index, problem)}
              </button>
            ))}
          </div>

          {test && (
            <section className="result-detail">
              <div className="result-detail-heading">
                <strong>{test.label}</strong>
                <span className={`test-status test-status-${test.status.toLowerCase()}`}>{statusLabel(test.status)}</span>
              </div>

              {test.hidden ? (
                <p className="hidden-result-copy">
                  {test.passed ? 'This hidden case passed.' : (test.error || 'This solution does not handle the hidden case.')}
                </p>
              ) : (
                <div className="result-values">
                  <div><span>Input</span><pre>{test.input || '""'}</pre></div>
                  <div><span>Expected</span><pre>{test.expected}</pre></div>
                  <div><span>Actual</span><pre>{test.actual || '(no output)'}</pre></div>
                </div>
              )}

              {!test.passed && !test.hidden && test.error && (
                <div className="execution-error"><strong>Error</strong><code>{test.error}</code></div>
              )}
              <div className="execution-time">{test.executionTimeMs} ms</div>
            </section>
          )}
        </>
      )}
    </div>
  )
}
