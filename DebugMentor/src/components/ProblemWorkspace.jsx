import CodeEditorPanel from './CodeEditorPanel'
import OutputPanel from './OutputPanel'
import ProblemStatement from './ProblemStatement'

export default function ProblemWorkspace({
  problem,
  code,
  language,
  activeTab,
  setActiveTab,
  isAnalyzing,
  isRunning,
  runResult,
  analysisResult,
  onBack,
  onCodeChange,
  onRun,
  onSubmit,
  revealHint,
  selectedVisibleTestCaseId,
  onSelectVisibleTestCase,
  loading = false,
}) {
  return (
    <main className="problem-workspace-shell">
      <header className="problem-workspace-header">
        <button type="button" className="back-to-explorer" onClick={onBack}>
          Back to Patterns
        </button>
        <div className="problem-workspace-heading">
          <div className="workspace-kicker">Practice Workspace</div>
          <h1>{problem?.title || 'Select a problem'}</h1>
          {problem?.pattern?.name && <p>{problem.pattern.name}</p>}
        </div>
        {problem?.difficulty && (
          <span className={`difficulty difficulty-${problem.difficulty}`}>{problem.difficulty}</span>
        )}
      </header>

      <div className="problem-workspace-grid">
        <ProblemStatement
          problem={problem}
          loading={loading}
          selectedVisibleTestCaseId={selectedVisibleTestCaseId}
          onSelectVisibleTestCase={onSelectVisibleTestCase}
        />

        <section className="workspace-editor-stack">
          <CodeEditorPanel
            code={code}
            language={language}
            isAnalyzing={isAnalyzing}
            isRunning={isRunning}
            onCodeChange={onCodeChange}
            onRun={onRun}
            onSubmit={onSubmit}
            analysisResult={analysisResult}
          />

          <OutputPanel
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            analysisResult={analysisResult}
            isAnalyzing={isAnalyzing}
            isRunning={isRunning}
            runResult={runResult}
            language={language}
            revealHint={revealHint}
            code={code}
          />
        </section>
      </div>
    </main>
  )
}
