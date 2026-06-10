export function getReadableErrorText(rawText = '', fallback = 'Execution failed.') {
  if (!rawText) return fallback

  const text = String(rawText).replace(/\r\n/g, '\n').trim()
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean)
  if (lines.length === 0) return fallback

  const compilerLine = lines.find((line) => line.includes(' error:') || line.startsWith('error:'))
  if (compilerLine) {
    return compilerLine
      .replace(/^[A-Za-z]:\\[^:]+:\d+:\d+:\s*/, '')
      .replace('error:', 'Error:')
      .trim()
  }

  const runtimeLine = [...lines].reverse().find((line) =>
    /TypeError|NameError|ValueError|IndexError|KeyError|ZeroDivisionError|AttributeError|RecursionError|RuntimeError|SyntaxError/.test(line)
  )
  if (runtimeLine) return runtimeLine

  return lines[0]
}

export function getErrorHeadline(runResult) {
  const stage = runResult?.errorStage
  if (stage === 'compile') return 'Compile Error'
  if (runResult?.dominantFailureType === 'COMPILE_ERROR') return 'Compile Error'
  if (runResult?.dominantFailureType === 'TIMEOUT') return 'Timeout'
  return 'Runtime Error'
}
