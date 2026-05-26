export default function HintCard({ hint, revealed }) {
  const isLocked = !revealed
  const isSolution = hint.level === 3

  const renderText = (text) => {
    if (!text || typeof text !== 'string') return <span>No hint text available.</span>
    const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/)
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i}>{part.slice(1, -1)}</code>
      }
      return <span key={i}>{part}</span>
    })
  }

  return (
    <div
      id={`hint-card-${hint.level}`}
      className={`hint-card ${isLocked ? 'locked' : ''} ${isSolution ? 'solution-card' : ''}`}
    >
      <div className="hint-card-header">
        <span className={`hint-badge ${isSolution ? 'solution' : ''}`}>
          {isSolution ? 'SOL' : `H${hint.level}`}
        </span>
        <span className="hint-title">{hint.title}</span>
        {isLocked && <span className="hint-lock-icon">Locked</span>}
      </div>

      {isLocked ? (
        <div className="hint-locked-text">
          {isSolution ? 'Confirm to unlock the reference solution.' : 'Unlock to see this hint.'}
        </div>
      ) : isSolution ? (
        <pre className="solution-code-block">{hint.text}</pre>
      ) : (
        <p className="hint-text">{renderText(hint.text)}</p>
      )}
    </div>
  )
}
