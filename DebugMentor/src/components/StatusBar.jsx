// StatusBar.jsx — Phase 2
// Shows: language pill, AST issue count, line/col, status indicator
import { languageConfig } from '../data/mockData'

export default function StatusBar({ language, isAnalyzing, analysisResult }) {
  const cfg = languageConfig[language]

  let statusClass = 'ready'
  let statusIcon = '●'
  let statusText = 'Ready'

  if (isAnalyzing) {
    statusClass = 'analyzing'
    statusIcon = '⟳'
    statusText = 'Analyzing...'
  } else if (analysisResult) {
    statusClass = 'complete'
    statusIcon = '✓'
    statusText = 'Analysis Complete'
  }

  // Phase 2: AST issue count (from real analysis, not mock test cases)
  const astCount = analysisResult?.astIssues?.length ?? 0
  const failedTests = analysisResult?.failedCount ?? 0
  const totalIssues = astCount + failedTests

  return (
    <div className="status-bar">
      {/* Left: language pill */}
      <div className="status-pill-bar">
        <span className="sdot" />
        {cfg.label} {cfg.version}
      </div>

      {/* AST issue count */}
      {analysisResult && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          fontSize: 11,
          fontFamily: 'var(--font-mono)',
        }}>
          {astCount > 0 && (
            <span style={{
              display: 'flex', alignItems: 'center', gap: 4,
              color: 'var(--accent-secondary)',
            }}>
              <span style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'var(--accent-secondary)',
                display: 'inline-block',
                boxShadow: '0 0 6px var(--accent-secondary)',
              }} />
              {astCount} AST {astCount === 1 ? 'Issue' : 'Issues'}
            </span>
          )}
          {failedTests > 0 && (
            <span style={{
              display: 'flex', alignItems: 'center', gap: 4,
              color: 'var(--accent-danger)',
            }}>
              <span style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'var(--accent-danger)',
                display: 'inline-block',
                boxShadow: '0 0 6px var(--accent-danger)',
              }} />
              {failedTests} Test {failedTests === 1 ? 'Failure' : 'Failures'}
            </span>
          )}
          {totalIssues === 0 && (
            <span style={{
              display: 'flex', alignItems: 'center', gap: 4,
              color: 'var(--accent-primary)',
            }}>
              <span style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'var(--accent-primary)',
                display: 'inline-block',
                boxShadow: '0 0 6px var(--accent-primary)',
              }} />
              All Clear
            </span>
          )}
        </div>
      )}

      {/* Center: version info */}
      <div className="status-center">
        UTF-8 · LF · Practice Mode
      </div>

      {/* Right: status indicator */}
      <div className="status-right">
        <div className={`status-indicator ${statusClass}`} id="status-indicator">
          <span className="idot" />
          <span>{statusText}</span>
        </div>
      </div>
    </div>
  )
}
