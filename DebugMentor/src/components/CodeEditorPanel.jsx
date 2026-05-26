import { useRef, useState, useCallback } from 'react'
import MonacoEditor from '@monaco-editor/react'
import { languageConfig } from '../data/mockData'
import { useTheme } from '../context/ThemeContext'

const MONACO_DARK = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '6B7280', fontStyle: 'italic' },
    { token: 'keyword', foreground: '93C5FD', fontStyle: 'bold' },
    { token: 'string', foreground: 'A7F3D0' },
    { token: 'number', foreground: 'FCD34D' },
    { token: 'function', foreground: 'C4B5FD' },
  ],
  colors: {
    'editor.background': '#111827',
    'editor.foreground': '#F3F4F6',
    'editor.lineHighlightBackground': '#1F2937',
    'editor.selectionBackground': '#2563EB33',
    'editorLineNumber.foreground': '#6B7280',
    'editorLineNumber.activeForeground': '#CBD5E1',
    'editorCursor.foreground': '#60A5FA',
  },
}

const MONACO_LIGHT = {
  base: 'vs',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '94A3B8', fontStyle: 'italic' },
    { token: 'keyword', foreground: '2563EB', fontStyle: 'bold' },
    { token: 'string', foreground: '047857' },
    { token: 'number', foreground: 'B45309' },
    { token: 'function', foreground: '7C3AED' },
  ],
  colors: {
    'editor.background': '#FFFFFF',
    'editor.foreground': '#111827',
    'editor.lineHighlightBackground': '#F8FAFC',
    'editor.selectionBackground': '#2563EB22',
    'editorLineNumber.foreground': '#94A3B8',
    'editorLineNumber.activeForeground': '#475569',
    'editorCursor.foreground': '#2563EB',
  },
}

const fileNames = {
  python: 'solution.py',
  cpp: 'solution.cpp',
  java: 'Solution.java',
  javascript: 'solution.js',
}

export default function CodeEditorPanel({
  code,
  language,
  isAnalyzing,
  isRunning,
  onCodeChange,
  onRun,
  onSubmit,
  analysisResult,
}) {
  const editorRef = useRef(null)
  const [lineCol, setLineCol] = useState({ line: 1, col: 1 })
  const { theme } = useTheme()
  const cfg = languageConfig[language]
  const fileName = fileNames[language] || 'solution.py'
  const monacoTheme = theme === 'light' ? 'debugmentor-light' : 'debugmentor-dark'

  const handleEditorMount = useCallback((editor, monaco) => {
    editorRef.current = editor

    monaco.editor.defineTheme('debugmentor-dark', MONACO_DARK)
    monaco.editor.defineTheme('debugmentor-light', MONACO_LIGHT)
    monaco.editor.setTheme(monacoTheme)

    editor.onDidChangeCursorPosition((event) => {
      setLineCol({ line: event.position.lineNumber, col: event.position.column })
    })
  }, [monacoTheme])

  const issueCount = analysisResult?.astIssues?.length || 0
  const failureCount = analysisResult?.failedCount || 0
  const statusLabel = analysisResult
    ? (analysisResult.status === 'clean' ? 'Ready' : `${issueCount + failureCount} issue${issueCount + failureCount === 1 ? '' : 's'}`)
    : 'Practice'

  return (
    <div className="editor-panel" style={{ width: '100%' }}>
      <div className="breadcrumb-bar" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="crumb-file">{fileName}</span>
          <span
            style={{
              padding: '3px 8px',
              borderRadius: 999,
              border: '1px solid var(--border)',
              color: 'var(--text-secondary)',
              fontSize: 11,
              fontFamily: 'var(--font-mono)',
            }}
          >
            {statusLabel}
          </span>
        </div>
        <div style={{ color: 'var(--text-secondary)', fontSize: 11 }}>
          {cfg.label}
        </div>
      </div>

      <div className="editor-container">
        <MonacoEditor
          height="100%"
          language={cfg.monacoLang}
          value={code}
          theme={monacoTheme}
          onChange={(value) => onCodeChange(value || '')}
          onMount={handleEditorMount}
          options={{
            fontSize: 14,
            fontFamily: "'JetBrains Mono', 'Monaco', 'Courier New', monospace",
            lineNumbers: 'on',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            padding: { top: 14, bottom: 14 },
            folding: true,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            wordWrap: 'off',
            renderLineHighlight: 'gutter',
            overviewRulerLanes: 0,
          }}
        />
      </div>

      <div className="editor-toolbar">
        <div className="lang-badge">{cfg.label}</div>

        <button
          id="btn-run-code"
          className="btn-run"
          onClick={onRun}
          disabled={isRunning || isAnalyzing}
        >
          {isRunning ? 'Running...' : 'Run'}
        </button>

        <button
          id="btn-submit-analysis"
          className={`btn-submit ${!isAnalyzing ? 'btn-submit-pulse' : ''}`}
          onClick={onSubmit}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? 'Submitting...' : 'Submit'}
        </button>
      </div>

      <div
        style={{
          height: 24,
          background: 'var(--bg-base)',
          borderTop: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 16px',
          gap: 16,
          flexShrink: 0,
          fontFamily: 'var(--font-mono)',
          fontSize: 11,
          color: 'var(--text-secondary)',
        }}
      >
        <span>Ln {lineCol.line}, Col {lineCol.col}</span>
        <span style={{ marginLeft: 'auto' }}>UTF-8</span>
      </div>
    </div>
  )
}
