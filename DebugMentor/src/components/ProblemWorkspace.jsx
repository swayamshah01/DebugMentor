import CodeEditorPanel from './CodeEditorPanel'
import OutputPanel from './OutputPanel'
import ProblemStatement from './ProblemStatement'


export default function ProblemWorkspace({
  problem,
  loading,
  code,
  language,
  selectedTestCase,
  selectedTestCaseId,
  activePanel,
  busyAction,
  gradeResult,
  submissionResult,
  hints,
  requestError,
  hintError,
  onCodeChange,
  onRun,
  onSubmit,
  onPanelChange,
  onSelectTestCase,
  onRequestHint,
}) {
  const selectedCaseNumber = Math.max(
    1,
    (problem?.test_cases || []).findIndex((item) => item.id === selectedTestCase?.id) + 1,
  )

  return (
    <main className="workspace-page">
      <div className="workspace-grid">
        <ProblemStatement problem={problem} loading={loading} />
        <div className="workspace-right">
          <CodeEditorPanel
            code={code}
            language={language}
            selectedCaseNumber={selectedCaseNumber}
            busyAction={busyAction}
            onCodeChange={onCodeChange}
            onRun={onRun}
            onSubmit={onSubmit}
          />
          <OutputPanel
            activePanel={activePanel}
            problem={problem}
            selectedTestCaseId={selectedTestCaseId}
            gradeResult={gradeResult}
            submissionResult={submissionResult}
            hints={hints}
            busyAction={busyAction}
            requestError={requestError}
            hintError={hintError}
            onPanelChange={onPanelChange}
            onSelectTestCase={onSelectTestCase}
            onRequestHint={onRequestHint}
          />
        </div>
      </div>
    </main>
  )
}
