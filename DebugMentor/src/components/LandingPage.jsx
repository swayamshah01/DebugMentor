import { useTheme } from '../context/ThemeContext'

export default function LandingPage({ onGetStarted }) {
  const { theme, toggleTheme } = useTheme()

  const features = [
    { icon: '⚡', title: 'Real Execution', desc: 'Python, JavaScript, C++ and Java all compile and run on a live backend — no simulations.' },
    { icon: '🧠', title: 'AI-Powered Hints', desc: 'Progressive, Socratic hints guide you to the solution without spoiling the learning.' },
    { icon: '🔒', title: 'Secure Sandbox', desc: 'Every code submission runs in an isolated environment with strict timeouts and safety checks.' },
    { icon: '📊', title: 'Instant Feedback', desc: 'See stdout, stderr, exit codes, and execution time the moment your code finishes.' },
  ]

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-base)',
      color: 'var(--text-primary)',
      fontFamily: 'var(--font-body)',
      overflow: 'auto',
    }}>
      {/* ── Navbar ── */}
      <nav style={{
        height: 64,
        display: 'flex',
        alignItems: 'center',
        padding: '0 32px',
        borderBottom: '1px solid var(--border)',
        position: 'sticky',
        top: 0,
        background: 'var(--bg-base)',
        zIndex: 50,
        backdropFilter: 'blur(12px)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: 'linear-gradient(135deg, var(--accent-primary) 0%, #00E87A 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 'bold', color: '#0D0F14',
            boxShadow: '0 0 16px rgba(79,255,176,0.35)',
          }}>&gt;_</div>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 18, fontWeight: 700, letterSpacing: '-0.02em' }}>
            Debug<span style={{ color: 'var(--accent-primary)' }}>Mentor</span>
          </span>
        </div>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12 }}>
          <button onClick={toggleTheme} style={{
            width: 36, height: 36, borderRadius: '50%',
            background: 'var(--bg-elevated)', border: '1px solid var(--border-bright)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', fontSize: 16, transition: 'all 0.2s',
          }}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>

          <button
            onClick={onGetStarted}
            style={{
              padding: '8px 20px',
              background: 'transparent',
              border: '1px solid var(--accent-primary)',
              borderRadius: 8,
              color: 'var(--accent-primary)',
              fontFamily: 'var(--font-body)',
              fontWeight: 600,
              fontSize: 14,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(79,255,176,0.08)'; e.currentTarget.style.boxShadow = '0 0 16px rgba(79,255,176,0.2)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.boxShadow = 'none' }}
          >
            Sign In
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section style={{
        maxWidth: 900,
        margin: '0 auto',
        padding: '100px 32px 80px',
        textAlign: 'center',
      }}>
        {/* Badge */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'var(--hint-glow)', border: '1px solid rgba(79,255,176,0.25)',
          borderRadius: 20, padding: '6px 16px', marginBottom: 32,
          fontFamily: 'var(--font-mono)', fontSize: 12,
          color: 'var(--accent-primary)',
        }} className="fade-in">
          <span style={{
            width: 7, height: 7, borderRadius: '50%',
            background: 'var(--accent-primary)',
            boxShadow: '0 0 6px var(--accent-primary)',
            animation: 'pulse-dot 2s ease-in-out infinite',
            display: 'inline-block',
          }} />
          Live Execution · AI Hints · Multi-Language
        </div>

        <h1 style={{
          fontSize: 'clamp(40px, 6vw, 72px)',
          fontWeight: 800,
          lineHeight: 1.1,
          letterSpacing: '-0.03em',
          marginBottom: 24,
          background: 'linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }} className="fade-in">
          Debug smarter,<br />learn faster.
        </h1>

        <p style={{
          fontSize: 20,
          color: 'var(--text-secondary)',
          maxWidth: 560,
          margin: '0 auto 48px',
          lineHeight: 1.7,
        }} className="fade-in">
          An AI-powered code debugging tutor that executes your code in real-time,
          then guides you to the fix — without handing you the answer.
        </p>

        <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            id="landing-get-started-btn"
            onClick={onGetStarted}
            style={{
              padding: '14px 36px',
              background: 'var(--accent-primary)',
              border: 'none',
              borderRadius: 10,
              color: '#0D0F14',
              fontFamily: 'var(--font-body)',
              fontWeight: 700,
              fontSize: 16,
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 0 24px rgba(79,255,176,0.4)',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 32px rgba(79,255,176,0.5)' }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 0 24px rgba(79,255,176,0.4)' }}
          >
            Get Started — It's Free
          </button>
        </div>
      </section>

      {/* ── Terminal Preview ── */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '0 32px 80px' }}>
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-bright)',
          borderRadius: 12,
          overflow: 'hidden',
          boxShadow: '0 20px 60px rgba(0,0,0,0.4), 0 0 0 1px rgba(79,255,176,0.05)',
        }}>
          {/* Titlebar */}
          <div style={{ 
            display: 'flex', alignItems: 'center', gap: 7, 
            padding: '12px 16px', 
            borderBottom: '1px solid var(--border)',
            background: 'var(--bg-elevated)',
          }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#FF5F6D', display: 'inline-block' }} />
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#FFB347', display: 'inline-block' }} />
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#4FFFB0', display: 'inline-block' }} />
            <span style={{ marginLeft: 8, fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>
              solution.py — DebugMentor
            </span>
          </div>
          {/* Code */}
          <pre style={{
            padding: '20px 24px',
            fontFamily: 'var(--font-mono)',
            fontSize: 14,
            lineHeight: 1.8,
            color: 'var(--text-primary)',
            margin: 0,
            overflowX: 'auto',
          }}>
{`  `}<span style={{ color: '#C792EA' }}>def</span><span style={{ color: 'var(--accent-primary)' }}> find_max</span><span style={{ color: '#89DDFF' }}>(arr):</span>{`
    `}<span style={{ color: 'var(--text-secondary)' }}># Bug: crashes on empty list</span>{`
    max_val `}<span style={{ color: '#89DDFF' }}>= arr</span><span style={{ color: '#F07178' }}>[0]</span>{`
    `}<span style={{ color: '#C792EA' }}>for</span>{` i `}<span style={{ color: '#C792EA' }}>in</span>{` range(len(arr)):
        `}<span style={{ color: '#C792EA' }}>if</span>{` arr[i] `}<span style={{ color: '#89DDFF' }}>&gt;</span>{` max_val:
            max_val `}<span style={{ color: '#89DDFF' }}>=</span>{` arr[i]
    `}<span style={{ color: '#C792EA' }}>return</span>{` max_val

`}<span style={{ color: 'var(--accent-danger)' }}>{`  ❌ IndexError: list index out of range`}</span>{`
`}<span style={{ color: 'var(--accent-primary)' }}>{`  💡 Hint: What happens when arr is empty?`}</span>
          </pre>
        </div>
      </section>

      {/* ── Features ── */}
      <section style={{ maxWidth: 900, margin: '0 auto', padding: '0 32px 100px' }}>
        <h2 style={{ textAlign: 'center', fontSize: 32, fontWeight: 700, marginBottom: 48, letterSpacing: '-0.02em' }}>
          Everything you need to level up
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 20,
        }}>
          {features.map(f => (
            <div
              key={f.title}
              style={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-bright)',
                borderRadius: 12,
                padding: '24px 20px',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'rgba(79,255,176,0.3)'
                e.currentTarget.style.boxShadow = '0 0 20px rgba(79,255,176,0.06)'
                e.currentTarget.style.transform = 'translateY(-3px)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'var(--border-bright)'
                e.currentTarget.style.boxShadow = 'none'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              <div style={{ fontSize: 28, marginBottom: 12 }}>{f.icon}</div>
              <div style={{ fontWeight: 700, marginBottom: 8, fontSize: 16 }}>{f.title}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: 13, lineHeight: 1.6 }}>{f.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{
        maxWidth: 700,
        margin: '0 auto 80px',
        padding: '0 32px',
        textAlign: 'center',
      }}>
        <div style={{
          background: 'var(--bg-elevated)',
          border: '1px solid rgba(79,255,176,0.2)',
          borderRadius: 16,
          padding: '48px 32px',
          boxShadow: '0 0 40px rgba(79,255,176,0.05)',
        }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, marginBottom: 12 }}>Ready to debug smarter?</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 28, fontSize: 15 }}>
            Create a free account and start running code in seconds.
          </p>
          <button
            id="landing-cta-btn"
            onClick={onGetStarted}
            style={{
              padding: '13px 32px',
              background: 'var(--accent-primary)',
              border: 'none',
              borderRadius: 8,
              color: '#0D0F14',
              fontWeight: 700,
              fontSize: 15,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(79,255,176,0.4)' }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
          >
            Create Free Account →
          </button>
        </div>
      </section>
    </div>
  )
}
