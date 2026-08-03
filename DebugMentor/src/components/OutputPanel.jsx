import HintsTab from './HintsTab'
import ResultPanel from './ResultPanel'
import TestCasesTab from './TestCasesTab'


export default function OutputPanel({
  activePanel,
  problem,
  selectedTestCaseId,
  gradeResult,
  submissionResult,
  hints,
  busyAction,
  requestError,
  hintError,
  onPanelChange,
  onSelectTestCase,
  onRequestHint,
}) {
  const tabs = [
    { id: 'tests', label: 'Test cases', badge: problem?.test_cases?.length || 0 },
    { id: 'result', label: 'Result', badge: gradeResult?.failedTests || null },
    { id: 'hints', label: 'Hints', badge: hints.length || null },
  ]

  return (
    <section className="practice-panel" aria-label="Practice feedback">
      <nav className="practice-tabs" role="tablist">
        {tabs.map((tab) => (
          <button
            type="button"
            role="tab"
            aria-selected={activePanel === tab.id}
            className={activePanel === tab.id ? 'active' : ''}
            key={tab.id}
            onClick={() => onPanelChange(tab.id)}
          >
            {tab.label}
            {tab.badge ? <span>{tab.badge}</span> : null}
          </button>
        ))}
      </nav>

      <div className="practice-panel-body">
        {activePanel === 'tests' && (
          <TestCasesTab
            problem={problem}
            selectedTestCaseId={selectedTestCaseId}
            onSelectTestCase={onSelectTestCase}
          />
        )}
        {activePanel === 'result' && (
          <ResultPanel result={gradeResult} requestError={requestError} />
        )}
        {activePanel === 'hints' && (
          <HintsTab
            submission={submissionResult}
            hints={hints}
            busy={busyAction === 'hint'}
            error={hintError}
            onRequestHint={onRequestHint}
          />
        )}
      </div>
    </section>
  )
}
