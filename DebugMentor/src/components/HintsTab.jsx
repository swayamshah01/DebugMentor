import { useState, useEffect } from 'react'
import HintCard from './HintCard'
import SolutionModal from './SolutionModal'

export function HintsTab({
  analysisResult,
  isAnalyzing,
  revealHint
}) {
  const [revealedLevel, setRevealedLevel] = useState(1);
  const [isRevealing, setIsRevealing] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (analysisResult?.submissionId) {
      setRevealedLevel(1);
    }
  }, [analysisResult?.submissionId]);

  if (isAnalyzing) {
    return (
      <div className="fade-in">
        <div className="skeleton" style={{ height: 80, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 100, marginBottom: 10 }} />
        <div className="skeleton" style={{ height: 100, marginBottom: 10, opacity: 0.6 }} />
      </div>
    )
  }

  if (!analysisResult) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🧠</div>
        <div className="empty-title">No hints yet</div>
        <div className="empty-desc">
          Submit a curated problem to see AI hints and feedback.
        </div>
      </div>
    )
  }

  const { hints, status, bugSummary } = analysisResult;
  const isClean = status === 'clean';

  if (isClean || !hints || (Array.isArray(hints) && hints.length === 0)) {
    return (
      <div className="fade-in">
        <div className="analysis-summary-card" style={isClean ? {
          borderColor: 'rgba(79, 255, 176, 0.25)',
          background: 'rgba(79, 255, 176, 0.04)'
        } : {}}>
          <div className="analysis-summary-label">● Static Analysis</div>
          <p className="analysis-summary-text">
            {isClean ? (
              <><span className="highlight green">✓ No issues detected</span> — your code is clean.</>
            ) : "No AI hints available."}
          </p>
        </div>
      </div>
    )
  }

  const handleReveal = async () => {
    if (revealedLevel >= 3) return;
    if (revealedLevel === 2) {
      setShowModal(true);
      return;
    }
    
    setIsRevealing(true);
    await revealHint(analysisResult.submissionId, null);
    setRevealedLevel(2);
    setIsRevealing(false);
  };

  const confirmSolution = async () => {
    setIsRevealing(true);
    setShowModal(false);
    await revealHint(analysisResult.submissionId, null);
    setRevealedLevel(3);
    setIsRevealing(false);
  };

  // Normalize offline array shape vs backend object shape
  const normHints = Array.isArray(hints) ? {
    explanation: bugSummary || "Offline mock analysis.",
    hint_1: hints[0]?.text || "",
    hint_2: hints[1]?.text || "",
    hint_3: hints[2]?.text || ""
  } : hints;

  return (
    <div className="fade-in">
      <div className="analysis-summary-card">
        <div className="analysis-summary-label">● AI Assistant</div>
        <p className="analysis-summary-text">
          {normHints.explanation}
        </p>
      </div>

      <div style={{ marginTop: 16 }}>
        {revealedLevel >= 1 && (
           <HintCard 
             hint={{ level: 1, icon: '🔍', title: 'Directional Nudge', text: normHints.hint_1 }} 
             revealed={true} 
           />
        )}
        {revealedLevel >= 2 && (
           <HintCard 
             hint={{ level: 2, icon: '🎯', title: 'Specific Guidance', text: normHints.hint_2 }} 
             revealed={true} 
           />
        )}
        {revealedLevel >= 3 && (
           <HintCard 
             hint={{ level: 3, icon: '💡', title: 'Solution Snippet', text: normHints.hint_3 }} 
             revealed={true} 
           />
        )}
      </div>

      {revealedLevel < 3 && (
        <button 
           onClick={handleReveal} 
           disabled={isRevealing}
           style={{
             marginTop: 16,
             width: '100%',
             padding: '12px',
             background: 'var(--bg-elevated)',
             border: '1px dashed var(--border-bright)',
             color: 'var(--text-primary)',
             borderRadius: '6px',
             cursor: isRevealing ? 'wait' : 'pointer'
           }}
        >
          {isRevealing ? 'Loading...' : `Reveal Next Hint (${3 - revealedLevel} left)`}
        </button>
      )}

      {showModal && (
        <SolutionModal 
           onCancel={() => setShowModal(false)}
           onReveal={confirmSolution} 
        />
      )}
    </div>
  )
}
