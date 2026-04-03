// SolutionModal.jsx
export default function SolutionModal({ onCancel, onReveal }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <span className="modal-icon">⚠️</span>
        <h2 className="modal-title">Reveal Full Solution?</h2>
        <p className="modal-text">
          Viewing the solution will be <span className="warning">logged and reported</span> to your instructor.
          We recommend trying once more with Hint 2 before revealing.
        </p>
        <div style={{
          background: 'rgba(255, 179, 71, 0.06)',
          border: '1px solid rgba(255, 179, 71, 0.2)',
          borderRadius: 6,
          padding: '10px 14px',
          marginBottom: 20,
          fontFamily: 'var(--font-body)',
          fontSize: 13,
          color: 'var(--accent-secondary)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: 8
        }}>
          <span>💡</span>
          <span>
            This action is irreversible for this session. Your attempt count is currently:{' '}
            <strong>2</strong>
          </span>
        </div>
        <div className="modal-actions">
          <button id="modal-cancel-btn" className="btn-modal-cancel" onClick={onCancel}>
            Cancel
          </button>
          <button id="modal-reveal-btn" className="btn-modal-reveal" onClick={onReveal}>
            🔓 Reveal Solution
          </button>
        </div>
      </div>
    </div>
  )
}
