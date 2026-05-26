export default function SolutionModal({ onCancel, onReveal }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-card" onClick={(event) => event.stopPropagation()}>
        <h2 className="modal-title">Show Reference Solution?</h2>
        <p className="modal-text">
          This will unlock the complete reference solution for this submission. Try the second hint first if you still want practice.
        </p>
        <div className="modal-actions">
          <button id="modal-cancel-btn" className="btn-modal-cancel" onClick={onCancel}>
            Keep Practicing
          </button>
          <button id="modal-reveal-btn" className="btn-modal-reveal" onClick={onReveal}>
            Show Solution
          </button>
        </div>
      </div>
    </div>
  )
}
