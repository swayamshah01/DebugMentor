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
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean)

  const paragraphs = String(problem.statement || '')
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)

  return (
    <aside className="problem-pane">
      <article className="problem-content">
        <header className="problem-heading">
          <div className="problem-meta">
            <span className="problem-pattern">{problem.pattern?.name}</span>
            <span className={`difficulty difficulty-${problem.difficulty}`}>{problem.difficulty}</span>
          </div>
          <h1>{problem.title}</h1>
        </header>

        <section className="statement-section statement-copy">
          {paragraphs.map((paragraph, index) => <p key={`${paragraph}-${index}`}>{paragraph}</p>)}
        </section>

        {problem.examples?.length > 0 && (
          <section className="statement-section">
            <h2>Examples</h2>
            <div className="example-list">
              {problem.examples.map((example, index) => (
                <div className="example-block" key={`${example.input}-${index}`}>
                  <h3>Example {index + 1}</h3>
                  <div className="example-value"><strong>Input:</strong><pre>{example.input}</pre></div>
                  <div className="example-value"><strong>Output:</strong><pre>{example.output}</pre></div>
                  {example.explanation && <p><strong>Explanation:</strong> {example.explanation}</p>}
                </div>
              ))}
            </div>
          </section>
        )}

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

        <section className="statement-section">
          <h2>Console input and output</h2>
          <div className="io-specification">
            <div>
              <h3>Input</h3>
              <pre>{problem.input_format || 'Read the values from standard input.'}</pre>
            </div>
            <div>
              <h3>Output</h3>
              <pre>{problem.output_format || 'Print the required answer.'}</pre>
            </div>
          </div>
        </section>
      </article>
    </aside>
  )
}
