export default function RecommendationPanel({ profile }) {
  if (!profile) return null

  const weakPatterns = profile.weak_patterns || []
  const recommendations = profile.recommendations || []
  const snapshot = profile.readiness_snapshot

  return (
    <section className="recommendation-panel">
      <div className="sidebar-section-title">Progress</div>
      <div className="mini-metrics">
        <div className="mini-metric">
          <span className="mini-value">{profile.stats?.passed_submissions || 0}</span>
          <span className="mini-label">Solved</span>
        </div>
        <div className="mini-metric">
          <span className="mini-value">{profile.stats?.pass_rate?.toFixed?.(0) || 0}%</span>
          <span className="mini-label">Pass rate</span>
        </div>
      </div>

      {snapshot && (
        <div className="snapshot-block">
          <div className="info-label">Readiness</div>
          <div className="snapshot-line">Strong: {snapshot.strongest_patterns?.join(', ') || '—'}</div>
          <div className="snapshot-line">Weak: {snapshot.weakest_patterns?.join(', ') || '—'}</div>
          <div className="snapshot-line">Streak: {snapshot.recent_streak || 0}</div>
        </div>
      )}

      {weakPatterns.length > 0 && (
        <div className="snapshot-block">
          <div className="info-label">Weak Patterns</div>
          {weakPatterns.slice(0, 3).map((item) => (
            <div key={item.pattern_id} className="snapshot-line">
              {item.pattern_name} · {item.mastery_percent.toFixed(0)}%
            </div>
          ))}
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="snapshot-block">
          <div className="info-label">Retry List</div>
          {recommendations.map((rec, index) => (
            <div key={index} className="snapshot-line">
              {rec.label}: {rec.title} {rec.reason ? `- ${rec.reason}` : ''}
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
