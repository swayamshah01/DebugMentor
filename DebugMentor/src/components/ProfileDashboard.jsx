import { useEffect, useMemo, useState } from 'react'

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'achievements', label: 'Achievements' },
  { id: 'history', label: 'History' },
  { id: 'insights', label: 'Insights' },
]

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' })
}

function toneClass(tone) {
  if (tone === 'success') return 'success'
  if (tone === 'warning') return 'warning'
  if (tone === 'accent') return 'accent'
  return 'neutral'
}

function buildActivityWeeks(submissions = [], weeks = 24) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const dayMap = new Map()
  submissions.forEach((submission) => {
    const key = new Date(submission.submitted_at).toISOString().slice(0, 10)
    dayMap.set(key, (dayMap.get(key) || 0) + 1)
  })

  const totalDays = weeks * 7
  const start = new Date(today)
  start.setDate(today.getDate() - (totalDays - 1))

  const cells = []
  for (let i = 0; i < totalDays; i += 1) {
    const current = new Date(start)
    current.setDate(start.getDate() + i)
    const key = current.toISOString().slice(0, 10)
    const count = dayMap.get(key) || 0
    let level = 0
    if (count >= 4) level = 4
    else if (count === 3) level = 3
    else if (count === 2) level = 2
    else if (count === 1) level = 1

    cells.push({
      key,
      level,
      count,
      dayLabel: current.toLocaleDateString([], { month: 'short', day: 'numeric' }),
      weekday: current.getDay(),
    })
  }

  const columns = []
  for (let index = 0; index < cells.length; index += 7) {
    columns.push(cells.slice(index, index + 7))
  }
  return columns
}

function buildRecentActivity(submissions = []) {
  return submissions.slice(0, 6).map((item) => ({
    id: item.submission_id,
    title: item.problem_title || `Submission ${item.submission_id}`,
    subtitle: item.pattern_name || item.language,
    status: item.status,
    note: item.mistake_type ? item.mistake_type.replaceAll('_', ' ') : 'Verified attempt logged',
    time: formatDate(item.submitted_at),
  }))
}

function calcSolvedByDifficulty(profile) {
  const solved = profile?.solved_problems_count || 0
  const total = profile?.stats?.total_submissions || 0
  const easy = Math.max(0, Math.round(solved * 0.5))
  const medium = Math.max(0, Math.round(solved * 0.35))
  const hard = Math.max(0, solved - easy - medium)
  return {
    easy,
    medium,
    hard,
    attempted: total,
  }
}

function CircularProgress({ value = 0 }) {
  const clamped = Math.max(0, Math.min(100, value))
  const degrees = Math.round((clamped / 100) * 360)
  return (
    <div
      className="profile-ring"
      style={{
        background: `conic-gradient(var(--accent-primary) 0deg ${degrees}deg, var(--border) ${degrees}deg 360deg)`,
      }}
    >
      <div className="profile-ring-inner">
        <div className="profile-ring-value">{clamped}%</div>
        <div className="profile-ring-label">pass rate</div>
      </div>
    </div>
  )
}

function BadgeTile({ badge }) {
  return (
    <article className={`profile-badge-tile ${toneClass(badge.tone)}`}>
      <div className="profile-badge-icon">{badge.icon}</div>
      <div>
        <h4>{badge.label}</h4>
        <p>{badge.description}</p>
      </div>
    </article>
  )
}

export function ProfileDashboard({ userId, username, fetchProfile, onBack, onLogout }) {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeSection, setActiveSection] = useState('dashboard')

  useEffect(() => {
    if (!userId) {
      setError('No user ID provided')
      setLoading(false)
      return
    }

    const loadProfile = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchProfile(userId)
        if (!data) {
          setError('Failed to load profile')
          return
        }
        setProfile(data)
      } catch (err) {
        setError(err.message || 'Error loading profile')
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [userId, fetchProfile])

  const activityWeeks = useMemo(() => buildActivityWeeks(profile?.submission_history || []), [profile])
  const recentActivity = useMemo(() => buildRecentActivity(profile?.submission_history || []), [profile])
  const solvedBreakdown = useMemo(() => calcSolvedByDifficulty(profile), [profile])
  const passRate = Math.round(profile?.stats?.pass_rate || 0)
  const streak = profile?.readiness_snapshot?.recent_streak || 0
  const strongestPatterns = profile?.readiness_snapshot?.strongest_patterns || []
  const weakestPatterns = profile?.readiness_snapshot?.weakest_patterns || []
  const solvedCount = profile?.solved_problems_count || 0
  const totalSubmissions = profile?.stats?.total_submissions || 0
  const averageHints = Number(profile?.readiness_snapshot?.average_hints || 0).toFixed(1)

  const renderDashboard = () => (
    <>
      <section className="profile-top-grid">
        <article className="profile-panel profile-identity-card">
          <div className="profile-avatar-shell">
            <div className="profile-avatar-large">
              {(username || profile?.username || 'DM').slice(0, 2).toUpperCase()}
            </div>
            <span className="profile-avatar-badge">DM</span>
          </div>

          <div className="profile-identity-block">
            <h1>{profile?.username || username || 'Student'}</h1>
            <div className="profile-handle">@{profile?.username || username || 'student'}</div>
            <div className="profile-rank-line">
              <span>Learning Profile</span>
              <strong>{solvedCount} solved</strong>
            </div>
          </div>

          <div className="profile-side-metrics">
            <div>
              <span>Pass rate</span>
              <strong>{passRate}%</strong>
            </div>
            <div>
              <span>Total submissions</span>
              <strong>{totalSubmissions}</strong>
            </div>
          </div>

          <button type="button" className="profile-primary-btn" onClick={onBack}>
            Back to Practice
          </button>

          <div className="profile-facts">
            <div>
              <span>Email</span>
              <strong>{profile?.email}</strong>
            </div>
            <div>
              <span>Joined</span>
              <strong>{profile?.created_at ? formatDate(profile.created_at) : '-'}</strong>
            </div>
            <div>
              <span>Average hints</span>
              <strong>{averageHints}</strong>
            </div>
          </div>
        </article>

        <article className="profile-panel profile-progress-card">
          <div className="profile-panel-header">
            <div>
              <div className="profile-kicker">Performance Snapshot</div>
              <h2>Practice momentum</h2>
            </div>
          </div>

          <div className="profile-progress-layout">
            <CircularProgress value={passRate} />

            <div className="profile-breakdown-list">
              <div className="profile-breakdown-item easy">
                <span>Easy solved</span>
                <strong>{solvedBreakdown.easy}</strong>
              </div>
              <div className="profile-breakdown-item medium">
                <span>Medium solved</span>
                <strong>{solvedBreakdown.medium}</strong>
              </div>
              <div className="profile-breakdown-item hard">
                <span>Hard solved</span>
                <strong>{solvedBreakdown.hard}</strong>
              </div>
              <div className="profile-breakdown-item neutral">
                <span>Attempts tracked</span>
                <strong>{solvedBreakdown.attempted}</strong>
              </div>
            </div>
          </div>
        </article>

        <article className="profile-panel profile-streak-card">
          <div className="profile-kicker">Current Streak</div>
          <div className="profile-streak-value">{streak} days</div>
          <div className="profile-streak-copy">
            Keep your run alive by getting another verified submit today.
          </div>

          <div className="profile-mini-progress">
            <div className="profile-mini-progress-bar">
              <span style={{ width: `${Math.min(100, streak * 10)}%` }} />
            </div>
            <div className="profile-mini-progress-label">
              {streak >= 5 ? 'Strong momentum' : 'Building momentum'}
            </div>
          </div>
        </article>
      </section>

      <section className="profile-wide-grid">
        <article className="profile-panel profile-activity-panel">
          <div className="profile-panel-header">
            <div>
              <div className="profile-kicker">Submission Activity</div>
              <h2>{totalSubmissions} tracked attempts</h2>
            </div>
            <div className="profile-panel-meta">
              <span>Visible streak: {streak}</span>
              <span>Last 24 weeks</span>
            </div>
          </div>

          <div className="profile-heatmap">
            {activityWeeks.map((week, columnIndex) => (
              <div key={`week-${columnIndex}`} className="profile-heatmap-column">
                {week.map((day) => (
                  <div
                    key={day.key}
                    className={`profile-heat-cell level-${day.level}`}
                    title={`${day.dayLabel}: ${day.count} submission${day.count === 1 ? '' : 's'}`}
                  />
                ))}
              </div>
            ))}
          </div>

          <div className="profile-legend">
            <span>Less</span>
            <div className="profile-legend-scale">
              <span className="profile-heat-cell level-0" />
              <span className="profile-heat-cell level-1" />
              <span className="profile-heat-cell level-2" />
              <span className="profile-heat-cell level-3" />
              <span className="profile-heat-cell level-4" />
            </div>
            <span>More</span>
          </div>
        </article>

        <article className="profile-panel profile-recent-panel">
          <div className="profile-panel-header">
            <div>
              <div className="profile-kicker">Recent Activity</div>
              <h2>Latest submissions</h2>
            </div>
          </div>

          <div className="profile-recent-list">
            {recentActivity.length > 0 ? recentActivity.map((item) => (
              <div key={item.id} className="profile-recent-item">
                <div className={`profile-recent-status ${item.status === 'passed' ? 'passed' : 'failed'}`}>
                  {item.status === 'passed' ? 'OK' : 'FIX'}
                </div>
                <div className="profile-recent-copy">
                  <div className="profile-recent-title">{item.title}</div>
                  <div className="profile-recent-subtitle">{item.subtitle}</div>
                  <div className="profile-recent-note">{item.note}</div>
                </div>
                <div className="profile-recent-time">{item.time}</div>
              </div>
            )) : (
              <div className="profile-empty-copy">No submissions yet.</div>
            )}
          </div>
        </article>
      </section>
    </>
  )

  const renderAchievements = () => (
    <section className="profile-split-grid">
      <article className="profile-panel">
        <div className="profile-panel-header">
          <div>
            <div className="profile-kicker">Achievements</div>
            <h2>Unlocked badges</h2>
          </div>
          <div className="profile-panel-meta">{profile?.badges?.length || 0} total</div>
        </div>
        <div className="profile-badge-grid">
          {(profile?.badges || []).length > 0 ? (
            profile.badges.map((badge) => <BadgeTile key={badge.id} badge={badge} />)
          ) : (
            <div className="profile-empty-copy">Solve more verified problems to unlock your first badge.</div>
          )}
        </div>
      </article>

      <article className="profile-panel">
        <div className="profile-panel-header">
          <div>
            <div className="profile-kicker">Strength Map</div>
            <h2>Pattern mastery</h2>
          </div>
        </div>
        <div className="profile-pattern-bars">
          {(profile?.weak_patterns || []).length > 0 ? profile.weak_patterns.map((item) => (
            <div key={item.pattern_id} className="profile-pattern-row">
              <div className="profile-pattern-row-top">
                <span>{item.pattern_name}</span>
                <strong>{item.mastery_percent.toFixed(0)}%</strong>
              </div>
              <div className="profile-pattern-bar">
                <span style={{ width: `${item.mastery_percent}%` }} />
              </div>
              <div className="profile-pattern-row-meta">
                {item.solved} solved / {item.attempted} attempted
              </div>
            </div>
          )) : (
            <div className="profile-empty-copy">Pattern mastery appears after a few tracked submissions.</div>
          )}
        </div>
      </article>
    </section>
  )

  const renderHistory = () => (
    <section className="profile-panel">
      <div className="profile-panel-header">
        <div>
          <div className="profile-kicker">History</div>
          <h2>Submission timeline</h2>
        </div>
      </div>
      <div className="profile-history-table">
        <div className="profile-history-head">
          <span>Problem</span>
          <span>Language</span>
          <span>Status</span>
          <span>Mistake type</span>
          <span>Submitted</span>
        </div>
        {(profile?.submission_history || []).length > 0 ? profile.submission_history.map((item) => (
          <div key={item.submission_id} className="profile-history-row">
            <div>
              <strong>{item.problem_title || `Submission ${item.submission_id}`}</strong>
              <small>{item.pattern_name || 'General'}</small>
            </div>
            <span>{item.language}</span>
            <span className={`profile-history-status ${item.status}`}>{item.status}</span>
            <span>{item.mistake_type ? item.mistake_type.replaceAll('_', ' ') : 'No logged mistake'}</span>
            <span>{formatDate(item.submitted_at)}</span>
          </div>
        )) : (
          <div className="profile-empty-copy padded">No history available yet.</div>
        )}
      </div>
    </section>
  )

  const renderInsights = () => (
    <section className="profile-split-grid">
      <article className="profile-panel">
        <div className="profile-panel-header">
          <div>
            <div className="profile-kicker">Debug Signals</div>
            <h2>Top repeated mistakes</h2>
          </div>
        </div>
        <div className="profile-insight-list">
          {(profile?.top_mistakes || []).length > 0 ? profile.top_mistakes.map((mistake) => (
            <div key={mistake.mistake_type} className="profile-insight-row">
              <span>{mistake.mistake_type.replaceAll('_', ' ')}</span>
              <strong>{mistake.count}x</strong>
            </div>
          )) : (
            <div className="profile-empty-copy">No repeated mistakes logged yet.</div>
          )}
        </div>
      </article>

      <article className="profile-panel">
        <div className="profile-panel-header">
          <div>
            <div className="profile-kicker">Readiness Snapshot</div>
            <h2>Where to push next</h2>
          </div>
        </div>
        <div className="profile-readiness-grid">
          <div className="profile-readiness-card">
            <span>Strongest patterns</span>
            <strong>{strongestPatterns.length ? strongestPatterns.join(', ') : '-'}</strong>
          </div>
          <div className="profile-readiness-card">
            <span>Weakest patterns</span>
            <strong>{weakestPatterns.length ? weakestPatterns.join(', ') : '-'}</strong>
          </div>
          <div className="profile-readiness-card">
            <span>Recommendations</span>
            <strong>
              {(profile?.recommendations || []).length
                ? profile.recommendations.map((item) => item.title).join(', ')
                : 'Keep practicing'}
            </strong>
          </div>
        </div>
      </article>
    </section>
  )

  const renderContent = () => {
    if (loading) {
      return <div className="profile-state-block">Loading your profile...</div>
    }
    if (error) {
      return <div className="profile-state-block error">{error}</div>
    }
    if (!profile) {
      return <div className="profile-state-block">No profile data available.</div>
    }
    if (activeSection === 'achievements') return renderAchievements()
    if (activeSection === 'history') return renderHistory()
    if (activeSection === 'insights') return renderInsights()
    return renderDashboard()
  }

  return (
    <main className="profile-page-shell">
      <div className="profile-layout">
        <aside className="profile-sidebar">
          <div className="profile-brand">DebugMentor</div>
          <div className="profile-sidebar-head">
            <div className="profile-sidebar-title">Learning Console</div>
            <div className="profile-sidebar-subtitle">Your coding progress hub</div>
          </div>

          <nav className="profile-side-nav">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`profile-side-nav-item ${activeSection === item.id ? 'active' : ''}`}
                onClick={() => setActiveSection(item.id)}
              >
                {item.label}
              </button>
            ))}
          </nav>

          <div className="profile-sidebar-footer">
            <button type="button" className="profile-secondary-btn" onClick={onBack}>
              Back to Practice
            </button>
            <button type="button" className="profile-danger-btn" onClick={onLogout}>
              Logout
            </button>
          </div>
        </aside>

        <section className="profile-main">
          <header className="profile-page-header">
            <div>
              <div className="profile-kicker">Profile</div>
              <h1>Track your DebugMentor journey</h1>
              <p>See streaks, badges, submissions, weak patterns, and where your interview prep is moving next.</p>
            </div>
          </header>

          <div className="profile-content">{renderContent()}</div>
        </section>
      </div>
    </main>
  )
}
