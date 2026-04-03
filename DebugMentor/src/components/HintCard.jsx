// HintCard.jsx
export default function HintCard({ hint, revealed, isLast }) {
  const isLocked = !revealed

  const renderText = (text) => {
    // Convert **bold** and `code` markdown to styled spans
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

  const isSolution = hint.level === 3

  return (
    <div
      id={`hint-card-${hint.level}`}
      className={`hint-card ${isLocked ? 'locked' : ''} ${isSolution ? 'solution-card' : ''}`}
    >
      <div className="hint-card-header">
        {isSolution ? (
          <span className="hint-badge solution">SOL</span>
        ) : (
          <span className="hint-badge">H{hint.level}</span>
        )}
        <span className="hint-title">
          {hint.icon} {hint.title}
        </span>
        {isLocked && <span className="hint-lock-icon">🔒</span>}
      </div>

      {isLocked ? (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          fontFamily: 'var(--font-body)',
          fontSize: 13,
          color: 'var(--text-secondary)',
          opacity: 0.7
        }}>
          <span>🔐</span>
          <span>{isSolution ? 'Requires confirmation to unlock' : 'Unlock to see hint'}</span>
        </div>
      ) : (
        <p className="hint-text">{renderText(hint.text)}</p>
      )}
    </div>
  )
}
