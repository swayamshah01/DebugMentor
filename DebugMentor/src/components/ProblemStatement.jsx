function MathText({ children }) {
  const parts = String(children || '').split(/(\^-?\d+)/g)
  return parts.map((part, index) => (
    /^\^-?\d+$/.test(part)
      ? <sup key={`${part}-${index}`}>{part.slice(1)}</sup>
      : <span key={`${part}-${index}`}>{part}</span>
  ))
}


export default function ProblemStatement({ problem, loading }) {
  if (loading || !problem) {
    return <aside className="problem-pane"><div className="page-state">Loading problem...</div></aside>
  }

  const constraints = String(problem.constraints || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

  return (
    <aside className="problem-pane">
      <article className="problem-content">
        <header className="problem-heading">
          <div className="problem-meta">
            <span>{problem.pattern?.name}</span>
            <span className={`difficulty difficulty-${problem.difficulty}`}>{problem.difficulty}</span>
          </div>
          <h1>{problem.title}</h1>
          {problem.short_description && <p className="problem-summary">{problem.short_description}</p>}
        </header>

        <section className="statement-section">
          <h2>Problem</h2>
          <p>{problem.statement}</p>
        </section>

        <section className="statement-section format-section">
          <div>
            <h2>Input format</h2>
            <pre>{problem.input_format || 'Read the values from standard input.'}</pre>
          </div>
          <div>
            <h2>Output format</h2>
            <pre>{problem.output_format || 'Print the required answer.'}</pre>
          </div>
        </section>

        {constraints.length > 0 && (
          <section className="statement-section">
            <h2>Constraints</h2>
            <ul className="constraint-list">
              {constraints.map((constraint, index) => (
                <li key={`${constraint}-${index}`}><MathText>{constraint}</MathText></li>
              ))}
            </ul>
          </section>
        )}

        {problem.examples?.length > 0 && (
          <section className="statement-section">
            <h2>Examples</h2>
            <div className="example-list">
              {problem.examples.map((example, index) => (
                <div className="example-block" key={`${example.input}-${index}`}>
                  <strong>Example {index + 1}</strong>
                  <dl>
                    <dt>Input</dt><dd><pre>{example.input}</pre></dd>
                    <dt>Output</dt><dd><pre>{example.output}</pre></dd>
                  </dl>
                  {example.explanation && <p>{example.explanation}</p>}
                </div>
              ))}
            </div>
          </section>
        )}
      </article>
    </aside>
  )
}
