import CodeEditorPanel from './CodeEditorPanel'
import OutputPanel from './OutputPanel'
import ProblemStatement from './ProblemStatement'

export default function ProblemWorkspace({
  problem,
  code,
  language,
  availableLanguages,
  activeTab,
  setActiveTab,
  isAnalyzing,
  isRunning,
  runResult,
  analysisResult,
  onCodeChange,
  onRun,
  onSubmit,
  onLanguageChange,
  revealHint,
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
            availableLanguages={availableLanguages}
            isAnalyzing={isAnalyzing}
            isRunning={isRunning}
            onCodeChange={onCodeChange}
            onRun={onRun}
            onSubmit={onSubmit}
            onLanguageChange={onLanguageChange}
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
            selectedVisibleTestCaseId={selectedVisibleTestCaseId}
            onSelectVisibleTestCase={onSelectVisibleTestCase}
          />
        </section>
      </div>
    </main>
  )
}
