import { OutputTab } from './OutputTab'
import { HintsTab } from './HintsTab'
import { TestCasesTab } from './TestCasesTab'

export default function OutputPanel({
  activeTab,
  setActiveTab,
  analysisResult,
  isAnalyzing,
  isRunning,
  runResult,
  language,
  revealHint,
}) {
  const astCount = analysisResult?.astIssues?.length ?? null
  const testCount = analysisResult?.testCases?.length ?? null

  const tabs = [
    { id: 'hints', label: 'Hints', badge: astCount },
    { id: 'output', label: 'Output', badge: null },
    { id: 'tests', label: 'Tests', badge: testCount },
  ]

  return (
    <div className="output-panel">
      <div className="panel-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            id={`tab-btn-${tab.id}`}
            className={`panel-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
            {tab.badge !== null && <span className="tab-count">{tab.badge}</span>}
          </button>
        ))}
      </div>

      <div className="panel-content">
        {activeTab === 'output' && (
          <OutputTab runResult={runResult} isRunning={isRunning} language={language} />
        )}
        {activeTab === 'hints' && (
          <HintsTab
            analysisResult={analysisResult}
            isAnalyzing={isAnalyzing}
            revealHint={revealHint}
          />
        )}
        {activeTab === 'tests' && (
          <TestCasesTab
            analysisResult={analysisResult}
            isAnalyzing={isAnalyzing}
          />
        )}
      </div>
    </div>
  )
}
