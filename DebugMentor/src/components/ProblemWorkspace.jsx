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
  onCodeChange,
  onRun,
  onSubmit,
  revealHint,
  onGenerateHints,
  selectedVisibleTestCaseId,
  onSelectVisibleTestCase,
  loading = false,
}) {
  return (
    <main className="problem-workspace-shell">
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
            problem={problem}
            analysisResult={analysisResult}
            isAnalyzing={isAnalyzing}
            isRunning={isRunning}
            runResult={runResult}
            language={language}
            revealHint={revealHint}
            onGenerateHints={onGenerateHints}
            selectedVisibleTestCaseId={selectedVisibleTestCaseId}
            onSelectVisibleTestCase={onSelectVisibleTestCase}
          />
        </section>
      </div>
    </main>
  )
}
