function parameterNames(inputFormat) {
  return [...String(inputFormat || '').matchAll(/Line\s+\d+:\s*([A-Za-z_][A-Za-z0-9_]*)/g)]
    .map((match) => match[1])
}


function formatInput(problem, rawInput) {
  const names = parameterNames(problem?.input_format)
  const lines = String(rawInput ?? '').replace(/\r/g, '').split('\n')
  return lines.map((line, index) => {
    const value = line === '' ? '""' : line
    return names[index] ? `${names[index]} = ${value}` : value
  }).join('\n')
}


export default function TestCasesTab({ problem, selectedTestCaseId, onSelectTestCase }) {
  const cases = problem?.test_cases || []
  const selectedIndex = Math.max(0, cases.findIndex((item) => item.id === selectedTestCaseId))
  const selected = cases[selectedIndex]

  if (!selected) {
    return <div className="panel-empty">No visible test cases are available.</div>
  }

  return (
    <div className="testcase-view">
      <div className="case-tabs" role="tablist" aria-label="Visible test cases">
        {cases.map((testCase, index) => (
          <button
            type="button"
            role="tab"
            aria-selected={testCase.id === selected.id}
            className={testCase.id === selected.id ? 'active' : ''}
            key={testCase.id}
            onClick={() => onSelectTestCase(testCase)}
          >
            Case {index + 1}
          </button>
        ))}
      </div>

      <section className="selected-case" aria-label={`Case ${selectedIndex + 1}`}>
        <div className="selected-case-heading">
          <strong>Case {selectedIndex + 1}</strong>
          <span>{selected.label}</span>
        </div>
        <div className="case-values">
          <div>
            <span>Input</span>
            <pre>{formatInput(problem, selected.input)}</pre>
          </div>
          <div>
            <span>Expected</span>
            <pre>{selected.expected_output}</pre>
          </div>
        </div>
      </section>
    </div>
  )
}
