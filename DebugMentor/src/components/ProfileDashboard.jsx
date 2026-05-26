import { useEffect, useState } from 'react'

export function ProfileDashboard({ userId, fetchProfile, token, onClose }) {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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

  const formatDate = (dateStr) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const renderContent = () => {
    if (loading) {
      return (
        <div style={{ padding: '40px 20px', textAlign: 'center' }}>
          <div style={{ opacity: 0.6 }}>Loading profile...</div>
        </div>
      )
    }

    if (error) {
      return (
        <div style={{
          padding: '20px',
          background: 'rgba(255,95,109,0.08)',
          border: '1px solid rgba(255,95,109,0.2)',
          borderRadius: 8,
          margin: 20,
          color: 'var(--accent-danger)',
        }}>
          ⚠ {error}
        </div>
      )
    }

    if (!profile) {
      return (
        <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          No profile data available
        </div>
      )
    }

    return (
      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Progress Summary */}
        <div style={{
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border)',
          borderRadius: 10,
          padding: 16,
        }}>
          <div style={{
            fontSize: 14,
            fontWeight: 700,
            color: 'var(--text-primary)',
            marginBottom: 12,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            opacity: 0.8,
          }}>
            📊 Progress Summary
          </div>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr 1fr',
            gap: 12,
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent-primary)' }}>
                {profile.stats.total_submissions}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 4 }}>
                Total Submissions
              </div>
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent-primary)' }}>
                {profile.stats.passed_submissions}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 4 }}>
                Passed
              </div>
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent-danger)' }}>
                {profile.stats.failed_submissions}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 4 }}>
                Failed
              </div>
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent-warning)' }}>
                {profile.stats.pass_rate.toFixed(1)}%
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 4 }}>
                Pass Rate
              </div>
            </div>
          </div>
        </div>

        {/* Weak Areas */}
        {profile.top_mistakes && profile.top_mistakes.length > 0 && (
          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              fontSize: 14,
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              opacity: 0.8,
            }}>
              ⚠ Weak Areas (Top Mistakes)
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {profile.top_mistakes.slice(0, 5).map((m, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 12px',
                    background: 'rgba(255,95,109,0.06)',
                    border: '1px solid rgba(255,95,109,0.15)',
                    borderRadius: 6,
                  }}
                >
                  <span style={{ color: 'var(--text-primary)', fontSize: 12 }}>
                    {m.mistake_type.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  <span style={{
                    background: 'rgba(255,95,109,0.2)',
                    color: 'var(--accent-danger)',
                    padding: '2px 8px',
                    borderRadius: 4,
                    fontSize: 11,
                    fontWeight: 600,
                  }}>
                    {m.count}x
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {profile.weak_patterns && profile.weak_patterns.length > 0 && (
          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              fontSize: 14,
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              opacity: 0.8,
            }}>
              🧭 Weak Patterns
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {profile.weak_patterns.slice(0, 5).map((item) => (
                <div key={item.pattern_id} style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                  <span style={{ color: 'var(--text-primary)', fontSize: 12 }}>{item.pattern_name}</span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{item.mastery_percent.toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {profile.recommendations && profile.recommendations.length > 0 && (
          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              fontSize: 14,
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              opacity: 0.8,
            }}>
              🎯 Retry Recommendations
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {profile.recommendations.map((item, index) => (
                <div key={index} style={{ padding: '8px 12px', borderRadius: 6, background: 'rgba(255,179,71,0.08)', border: '1px solid rgba(255,179,71,0.15)' }}>
                  <div style={{ color: 'var(--text-primary)', fontSize: 12, fontWeight: 600 }}>{item.label}: {item.title}</div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: 11, marginTop: 2 }}>{item.reason}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {profile.readiness_snapshot && (
          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              fontSize: 14,
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              opacity: 0.8,
            }}>
              🧪 Readiness Snapshot
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              <div>Strongest: {profile.readiness_snapshot.strongest_patterns.join(', ') || '—'}</div>
              <div>Weakest: {profile.readiness_snapshot.weakest_patterns.join(', ') || '—'}</div>
              <div>Recent streak: {profile.readiness_snapshot.recent_streak}</div>
              <div>Average hints: {profile.readiness_snapshot.average_hints.toFixed(1)}</div>
            </div>
          </div>
        )}

        {/* Recent Trend */}
        {profile.recent_trend && profile.recent_trend.length > 0 && (
          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              fontSize: 14,
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              opacity: 0.8,
            }}>
              📈 Recent Trend (Last 10 Submissions)
            </div>
            
            <div style={{
              display: 'flex',
              gap: 4,
              justifyContent: 'space-around',
              padding: '8px 0',
            }}>
              {profile.recent_trend.map((status, i) => (
                <div
                  key={i}
                  style={{
                    width: 24,
                    height: 24,
                    borderRadius: 4,
                    background: status === 'PASS'
                      ? 'rgba(79,255,176,0.2)'
                      : 'rgba(255,95,109,0.2)',
                    border: `1px solid ${status === 'PASS'
                      ? 'rgba(79,255,176,0.4)'
                      : 'rgba(255,95,109,0.4)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 12,
                    fontWeight: 700,
                    color: status === 'PASS'
                      ? 'var(--accent-primary)'
                      : 'var(--accent-danger)',
                  }}
                  title={status}
                >
                  {status === 'PASS' ? '✓' : '✗'}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Submission History */}
        {profile.submission_history && profile.submission_history.length > 0 && (
          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: 16,
            overflowY: 'auto',
            maxHeight: 400,
          }}>
            <div style={{
              fontSize: 14,
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              opacity: 0.8,
            }}>
              📋 Submission History (Latest 20)
            </div>
            
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
            }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ textAlign: 'left', padding: '8px 6px', color: 'var(--text-secondary)', fontWeight: 600 }}>ID</th>
                  <th style={{ textAlign: 'left', padding: '8px 6px', color: 'var(--text-secondary)', fontWeight: 600 }}>Language</th>
                  <th style={{ textAlign: 'left', padding: '8px 6px', color: 'var(--text-secondary)', fontWeight: 600 }}>Status</th>
                  <th style={{ textAlign: 'left', padding: '8px 6px', color: 'var(--text-secondary)', fontWeight: 600 }}>Mistake</th>
                  <th style={{ textAlign: 'left', padding: '8px 6px', color: 'var(--text-secondary)', fontWeight: 600 }}>Time</th>
                </tr>
              </thead>
              <tbody>
                {profile.submission_history.slice(0, 20).map((sub) => (
                  <tr key={sub.submission_id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '8px 6px', color: 'var(--text-primary)' }}>{sub.submission_id}</td>
                    <td style={{ padding: '8px 6px', color: 'var(--text-primary)' }}>{sub.language}</td>
                    <td style={{ padding: '8px 6px' }}>
                      <span style={{
                        padding: '2px 6px',
                        borderRadius: 3,
                        background: sub.status === 'passed'
                          ? 'rgba(79,255,176,0.15)'
                          : 'rgba(255,95,109,0.15)',
                        color: sub.status === 'passed'
                          ? 'var(--accent-primary)'
                          : 'var(--accent-danger)',
                        fontWeight: 600,
                        fontSize: 10,
                      }}>
                        {sub.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '8px 6px', color: 'var(--text-secondary)' }}>
                      {sub.mistake_type ? sub.mistake_type.replace(/_/g, ' ') : '—'}
                    </td>
                    <td style={{ padding: '8px 6px', color: 'var(--text-secondary)' }}>
                      {formatDate(sub.submitted_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {profile.submission_history && profile.submission_history.length === 0 && (
          <div style={{
            padding: '40px 20px',
            textAlign: 'center',
            color: 'var(--text-secondary)',
          }}>
            No submissions yet. Start by solving a problem!
          </div>
        )}
      </div>
    )
  }

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.6)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 20,
    }}>
      <div style={{
        background: 'var(--bg-primary)',
        borderRadius: 12,
        boxShadow: '0 20px 60px rgba(0,0,0,0.6)',
        width: '100%',
        maxWidth: 900,
        maxHeight: '90vh',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 20px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-elevated)',
          borderTopLeftRadius: 12,
          borderTopRightRadius: 12,
        }}>
          <div style={{
            fontSize: 18,
            fontWeight: 700,
            color: 'var(--text-primary)',
          }}>
            📚 Learning Profile
          </div>
          <button
            onClick={onClose}
            style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              background: 'transparent',
              border: '1px solid var(--border)',
              color: 'var(--text-secondary)',
              fontSize: 18,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'var(--bg-elevated)'
              e.currentTarget.style.borderColor = 'var(--accent-danger)'
              e.currentTarget.style.color = 'var(--accent-danger)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.color = 'var(--text-secondary)'
            }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div style={{
          overflowY: 'auto',
          flex: 1,
        }}>
          {renderContent()}
        </div>
      </div>
    </div>
  )
}
