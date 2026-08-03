function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}


export default function ProfileDashboard({ profile, loading, onRefresh, onPractice }) {
  if (loading || !profile) {
    return <main className="profile-page"><div className="page-state">Loading profile...</div></main>
  }

  const stats = profile.stats || {}
  const weakPatterns = profile.weak_patterns || []
  const history = profile.submission_history || []
  const streak = profile.readiness_snapshot?.recent_streak || 0

  return (
    <main className="profile-page">
      <header className="page-heading profile-heading">
        <div className="profile-identity">
          <span className="profile-avatar">{profile.username.slice(0, 1).toUpperCase()}</span>
          <div>
            <span className="eyebrow">Learning profile</span>
            <h1>{profile.username}</h1>
            <p>{profile.email}</p>
          </div>
        </div>
        <div className="profile-actions">
          <button className="button button-secondary" type="button" onClick={onRefresh}>Refresh</button>
          <button className="button button-primary" type="button" onClick={onPractice}>Practice</button>
        </div>
      </header>

      <section className="profile-stats" aria-label="Submission statistics">
        <div><span>Solved</span><strong>{profile.solved_problems_count || 0}</strong></div>
        <div><span>Submissions</span><strong>{stats.total_submissions || 0}</strong></div>
        <div><span>Pass rate</span><strong>{Math.round(stats.pass_rate || 0)}%</strong></div>
        <div><span>Current streak</span><strong>{streak} {streak === 1 ? 'day' : 'days'}</strong></div>
      </section>

      <div className="profile-grid">
        <section className="profile-section">
          <header><h2>Pattern progress</h2></header>
          {weakPatterns.length === 0 ? (
            <div className="panel-empty"><span>Complete a submission to start tracking progress.</span></div>
          ) : (
            <div className="mastery-list">
              {weakPatterns.map((item) => (
                <div className="mastery-row" key={item.pattern_id}>
                  <div>
                    <strong>{item.pattern_name}</strong>
                    <span>{item.solved} solved from {item.attempted} attempted</span>
                  </div>
                  <div className="mastery-value">{Math.round(item.mastery_percent)}%</div>
                  <div className="mastery-track"><span style={{ width: `${Math.max(2, item.mastery_percent)}%` }} /></div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="profile-section">
          <header><h2>Badges</h2></header>
          {(profile.badges || []).length === 0 ? (
            <div className="panel-empty"><span>Your first badge will appear after you begin practicing.</span></div>
          ) : (
            <div className="badge-list">
              {profile.badges.map((badge) => (
                <div className="badge-item" key={badge.id}>
                  <span>{badge.icon || badge.label.slice(0, 2).toUpperCase()}</span>
                  <div><strong>{badge.label}</strong><small>{badge.description}</small></div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <section className="profile-section history-section">
        <header><h2>Recent submissions</h2><span>{history.length} shown</span></header>
        {history.length === 0 ? (
          <div className="panel-empty">
            <strong>No submissions yet</strong>
            <button className="button button-secondary" type="button" onClick={onPractice}>Open practice</button>
          </div>
        ) : (
          <div className="history-table-wrap">
            <table className="history-table">
              <thead><tr><th>Problem</th><th>Pattern</th><th>Language</th><th>Status</th><th>Hints</th><th>Date</th></tr></thead>
              <tbody>
                {history.slice(0, 20).map((item) => (
                  <tr key={item.submission_id}>
                    <td>{item.problem_title || `Problem ${item.problem_id}`}</td>
                    <td>{item.pattern_name || '-'}</td>
                    <td>{item.language}</td>
                    <td><span className={`history-status ${item.status}`}>{item.status}</span></td>
                    <td>{item.hint_level}</td>
                    <td>{formatDate(item.submitted_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  )
}
