import { useEffect, useMemo, useState } from 'react'

const tabButtonStyle = (active) => ({
  border: '1px solid var(--border)',
  background: active ? 'var(--accent-primary)' : 'var(--bg-surface)',
  color: active ? '#fff' : 'var(--text-secondary)',
  borderRadius: 999,
  padding: '8px 14px',
  fontSize: 12,
  fontWeight: 700,
  cursor: 'pointer',
})

const cardStyle = {
  background: 'var(--bg-elevated)',
  border: '1px solid var(--border)',
  borderRadius: 14,
  padding: 18,
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function toneStyles(tone) {
  if (tone === 'success') {
    return {
      bg: 'rgba(34,197,94,0.08)',
      border: 'rgba(34,197,94,0.22)',
      text: '#22c55e',
    }
  }
  if (tone === 'warning') {
    return {
      bg: 'rgba(245,158,11,0.08)',
      border: 'rgba(245,158,11,0.22)',
      text: '#f59e0b',
    }
  }
  if (tone === 'accent') {
    return {
      bg: 'rgba(59,130,246,0.08)',
      border: 'rgba(59,130,246,0.22)',
      text: 'var(--accent-primary)',
    }
  }
  return {
    bg: 'var(--bg-surface)',
    border: 'var(--border)',
    text: 'var(--text-primary)',
  }
}

function BadgeCard({ badge }) {
  const tone = toneStyles(badge.tone)
  return (
    <div style={{
      background: tone.bg,
      border: `1px solid ${tone.border}`,
      borderRadius: 14,
      padding: 16,
      display: 'flex',
      flexDirection: 'column',
      gap: 10,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 42,
          height: 42,
          borderRadius: 12,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'var(--font-mono)',
          fontSize: 13,
          fontWeight: 800,
          background: 'rgba(255,255,255,0.08)',
          color: tone.text,
        }}>
          {badge.icon}
        </div>
        <div>
          <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{badge.label}</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{badge.description}</div>
        </div>
      </div>
    </div>
  )
}

export function ProfileDashboard({ userId, username, fetchProfile, onClose, onLogout }) {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

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
        if (data) {
          setProfile(data)
        } else {
          setError('Failed to load profile')
        }
      } catch (err) {
        setError(err.message || 'Error loading profile')
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [userId, fetchProfile])

  const heroStats = useMemo(() => {
    if (!profile) return []
    return [
      { label: 'Current streak', value: profile.readiness_snapshot?.recent_streak ?? 0, hint: 'Passed submissions in a row' },
      { label: 'Solved', value: profile.solved_problems_count ?? 0, hint: 'Unique problems accepted' },
      { label: 'Pass rate', value: `${Math.round(profile.stats?.pass_rate ?? 0)}%`, hint: 'Across graded submissions' },
      { label: 'Badges', value: profile.badges?.length ?? 0, hint: 'Custom milestones unlocked' },
    ]
  }, [profile])

  const renderOverview = () => (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 14 }}>
        {heroStats.map((item) => (
          <div key={item.label} style={cardStyle}>
            <div style={{ color: 'var(--text-secondary)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{item.label}</div>
            <div style={{ fontSize: 30, fontWeight: 800, margin: '10px 0 6px' }}>{item.value}</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{item.hint}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 14 }}>
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <div style={{ fontWeight: 700 }}>Recent form</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>Last 10 submissions</div>
          </div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {(profile.recent_trend || []).length > 0 ? profile.recent_trend.map((status, index) => (
              <div
                key={`${status}-${index}`}
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: 12,
                  background: status === 'PASS' ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
                  border: `1px solid ${status === 'PASS' ? 'rgba(34,197,94,0.24)' : 'rgba(239,68,68,0.24)'}`,
                  color: status === 'PASS' ? '#22c55e' : '#ef4444',
                }}
                title={status}
              >
                {status === 'PASS' ? 'P' : 'F'}
              </div>
            )) : <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>No submissions yet.</div>}
          </div>
        </div>

        <div style={cardStyle}>
          <div style={{ fontWeight: 700, marginBottom: 12 }}>Account</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13 }}>
            <div><strong>Username:</strong> {profile.username}</div>
            <div><strong>Email:</strong> {profile.email}</div>
            <div><strong>Joined:</strong> {formatDate(profile.created_at)}</div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        <div style={cardStyle}>
          <div style={{ fontWeight: 700, marginBottom: 12 }}>Weak patterns</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {(profile.weak_patterns || []).slice(0, 5).map((item) => (
              <div key={item.pattern_id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span>{item.pattern_name}</span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{item.mastery_percent.toFixed(0)}%</span>
                </div>
                <div style={{ height: 8, borderRadius: 999, background: 'var(--bg-surface)', overflow: 'hidden' }}>
                  <div style={{ width: `${item.mastery_percent}%`, height: '100%', background: 'var(--accent-primary)' }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={cardStyle}>
          <div style={{ fontWeight: 700, marginBottom: 12 }}>Recommendations</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {(profile.recommendations || []).length > 0 ? profile.recommendations.map((item, index) => (
              <div key={`${item.title}-${index}`} style={{ padding: 12, borderRadius: 12, background: 'var(--bg-surface)', border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 700 }}>{item.label}: {item.title}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginTop: 4 }}>{item.reason}</div>
              </div>
            )) : <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>No recommendations yet.</div>}
          </div>
        </div>
      </div>
    </>
  )

  const renderBadges = () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 14 }}>
      {(profile.badges || []).length > 0 ? profile.badges.map((badge) => (
        <BadgeCard key={badge.id} badge={badge} />
      )) : (
        <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Solve and submit more problems to unlock badges.</div>
      )}
    </div>
  )

  const renderHistory = () => (
    <div style={{ ...cardStyle, padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: 18, borderBottom: '1px solid var(--border)', fontWeight: 700 }}>Submission history</div>
      <div style={{ maxHeight: 520, overflowY: 'auto' }}>
        {(profile.submission_history || []).length > 0 ? profile.submission_history.map((sub) => (
          <div key={sub.submission_id} style={{ padding: 16, borderBottom: '1px solid var(--border)', display: 'grid', gridTemplateColumns: '1.2fr 0.9fr 0.9fr 1fr 1.2fr', gap: 12, alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 700 }}>{sub.problem_title || `Submission ${sub.submission_id}`}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{sub.pattern_name || 'General'}</div>
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{sub.language}</div>
            <div>
              <span style={{
                padding: '4px 8px',
                borderRadius: 999,
                background: sub.status === 'passed' ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
                color: sub.status === 'passed' ? '#22c55e' : '#ef4444',
                fontSize: 11,
                fontWeight: 700,
              }}>
                {sub.status.toUpperCase()}
              </span>
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{sub.mistake_type ? sub.mistake_type.replaceAll('_', ' ') : 'No logged mistake'}</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{formatDate(sub.submitted_at)}</div>
          </div>
        )) : (
          <div style={{ padding: 18, color: 'var(--text-secondary)', fontSize: 13 }}>No submissions yet.</div>
        )}
      </div>
    </div>
  )

  const renderInsights = () => (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
      <div style={cardStyle}>
        <div style={{ fontWeight: 700, marginBottom: 12 }}>Top mistakes</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {(profile.top_mistakes || []).length > 0 ? profile.top_mistakes.map((mistake) => (
            <div key={mistake.mistake_type} style={{ display: 'flex', justifyContent: 'space-between', padding: 12, borderRadius: 12, background: 'var(--bg-surface)', border: '1px solid var(--border)' }}>
              <span>{mistake.mistake_type.replaceAll('_', ' ')}</span>
              <span style={{ color: 'var(--accent-danger)', fontWeight: 700 }}>{mistake.count}x</span>
            </div>
          )) : <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>No mistakes logged yet.</div>}
        </div>
      </div>

      <div style={cardStyle}>
        <div style={{ fontWeight: 700, marginBottom: 12 }}>Readiness snapshot</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, color: 'var(--text-secondary)', fontSize: 13 }}>
          <div><strong style={{ color: 'var(--text-primary)' }}>Strongest:</strong> {(profile.readiness_snapshot?.strongest_patterns || []).join(', ') || '—'}</div>
          <div><strong style={{ color: 'var(--text-primary)' }}>Weakest:</strong> {(profile.readiness_snapshot?.weakest_patterns || []).join(', ') || '—'}</div>
          <div><strong style={{ color: 'var(--text-primary)' }}>Average hints:</strong> {(profile.readiness_snapshot?.average_hints || 0).toFixed(1)}</div>
          <div><strong style={{ color: 'var(--text-primary)' }}>Recent streak:</strong> {profile.readiness_snapshot?.recent_streak || 0}</div>
        </div>
      </div>
    </div>
  )

  const renderBody = () => {
    if (loading) {
      return <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-secondary)' }}>Loading profile...</div>
    }
    if (error) {
      return <div style={{ padding: 24, color: 'var(--accent-danger)' }}>{error}</div>
    }
    if (!profile) {
      return <div style={{ padding: 24, color: 'var(--text-secondary)' }}>No profile data available.</div>
    }

    if (activeTab === 'overview') return renderOverview()
    if (activeTab === 'badges') return renderBadges()
    if (activeTab === 'history') return renderHistory()
    return renderInsights()
  }

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.66)',
      zIndex: 1000,
      padding: 24,
      display: 'flex',
      alignItems: 'stretch',
      justifyContent: 'center',
    }}>
      <div style={{
        width: 'min(1280px, 100%)',
        background: 'var(--bg-base)',
        border: '1px solid var(--border)',
        borderRadius: 18,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxShadow: '0 28px 80px rgba(0,0,0,0.32)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '20px 24px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-surface)',
        }}>
          <div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Profile</div>
            <div style={{ fontSize: 28, fontWeight: 800, marginTop: 4 }}>{username || profile?.username || 'Student'}</div>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button type="button" onClick={() => setActiveTab('overview')} style={tabButtonStyle(activeTab === 'overview')}>Overview</button>
            <button type="button" onClick={() => setActiveTab('badges')} style={tabButtonStyle(activeTab === 'badges')}>Badges</button>
            <button type="button" onClick={() => setActiveTab('history')} style={tabButtonStyle(activeTab === 'history')}>History</button>
            <button type="button" onClick={() => setActiveTab('insights')} style={tabButtonStyle(activeTab === 'insights')}>Insights</button>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button
              type="button"
              onClick={onLogout}
              style={{
                border: '1px solid rgba(239,68,68,0.28)',
                background: 'rgba(239,68,68,0.08)',
                color: '#ef4444',
                borderRadius: 10,
                padding: '10px 14px',
                cursor: 'pointer',
                fontWeight: 700,
              }}
            >
              Logout
            </button>
            <button
              type="button"
              onClick={onClose}
              style={{
                border: '1px solid var(--border)',
                background: 'var(--bg-surface)',
                color: 'var(--text-primary)',
                borderRadius: 10,
                padding: '10px 14px',
                cursor: 'pointer',
                fontWeight: 700,
              }}
            >
              Close
            </button>
          </div>
        </div>

        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: 24,
          display: 'flex',
          flexDirection: 'column',
          gap: 14,
        }}>
          {renderBody()}
        </div>
      </div>
    </div>
  )
}
