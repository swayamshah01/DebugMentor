// StatusBar.jsx
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

  const errCount = analysisResult
    ? analysisResult.testCases.filter(t => !t.passed).length
    : 1

  return (
    <div className="status-bar">
      {/* Left: language pill */}
      <div className="status-pill-bar">
        <span className="sdot" />
        {cfg.label} {cfg.version}
      </div>



      {/* Error count */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 5,
        fontSize: 11,
        fontFamily: 'var(--font-mono)',
        color: 'var(--accent-danger)'
      }}>
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-danger)', display: 'inline-block' }} />
        {errCount} Error{errCount !== 1 ? 's' : ''}
      </div>

      {/* Center: line/col */}
      <div className="status-center">
        Ln 4, Col 19 · UTF-8
      </div>

      {/* Right: status indicator */}
      <div className="status-right">
        {analysisResult && (
          <>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>
              Hints: {' '}
              <span style={{ color: 'var(--accent-secondary)' }}>1/3</span>
            </span>
            <span style={{ color: 'var(--border-bright)' }}>·</span>
            <span>Attempts: 2</span>
            <span style={{ color: 'var(--border-bright)' }}>·</span>
            <span>Last saved 2m ago</span>
            <span style={{ color: 'var(--border-bright)' }}>·</span>
          </>
        )}
        <div className={`status-indicator ${statusClass}`} id="status-indicator">
          <span className="idot" />
          <span>{statusText}</span>
        </div>
      </div>
    </div>
  )
}
