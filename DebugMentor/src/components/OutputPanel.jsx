import { useState } from 'react'
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
  revealedHints,
  showSolutionModal,
  onNextHint,
  onShowSolutionModal,
  onCancelModal,
  onRevealSolution,
}) {
  const tabs = [
    { id: 'hints',  label: 'Hints',   badge: analysisResult ? analysisResult.hints.length : null },
    { id: 'output', label: 'Output',  badge: null },
    { id: 'tests',  label: 'Tests',   badge: analysisResult ? analysisResult.testCases.length : null },
  ]

  return (
    <div className="output-panel">
      {/* Tab bar */}
      <div className="panel-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            id={`tab-btn-${tab.id}`}
            className={`panel-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
            {tab.badge !== null && (
              <span className="tab-count">{tab.badge}</span>
            )}
          </button>
        ))}

        {/* AI Badge */}
        <div className="ai-badge">
          <span className="ai-badge-dot" />
          AI · Static + Runtime
        </div>
      </div>

      {/* Panel content */}
      <div className="panel-content">
        {activeTab === 'output' && (
          <OutputTab runResult={runResult} isRunning={isRunning} />
        )}
        {activeTab === 'hints' && (
          <HintsTab
            analysisResult={analysisResult}
            isAnalyzing={isAnalyzing}
            revealedHints={revealedHints}
            showSolutionModal={showSolutionModal}
            onNextHint={onNextHint}
            onShowSolutionModal={onShowSolutionModal}
            onCancelModal={onCancelModal}
            onRevealSolution={onRevealSolution}
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
