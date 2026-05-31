import { useRef, useState, useCallback } from 'react'
import MonacoEditor from '@monaco-editor/react'
import { languageConfig } from '../data/languages'
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
  const hasCode = Boolean(code?.trim())

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
      <div className="file-tabbar">
        <div className="file-tab active static-file-tab">
          <span className="file-tab-dot" style={{ background: cfg.color }} />
          <span>{fileName}</span>
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
            fontFamily: "Consolas, 'Courier New', monospace",
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
        {!hasCode && (
          <div className="editor-empty-overlay">
            Select a question and wait for the starter code to load.
          </div>
        )}
      </div>

      <div className="editor-toolbar">
        <div className="editor-meta-group">
          <div className="lang-badge">{cfg.label}</div>
          <div className="editor-status-pill">{statusLabel}</div>
        </div>

        <button
          type="button"
          id="btn-run-code"
          className="btn-run"
          onClick={onRun}
          disabled={!hasCode || isRunning || isAnalyzing}
        >
          {isRunning ? 'Running...' : 'Run'}
        </button>

        <button
          type="button"
          id="btn-submit-analysis"
          className={`btn-submit ${!isAnalyzing ? 'btn-submit-pulse' : ''}`}
          onClick={onSubmit}
          disabled={!hasCode || isAnalyzing || isRunning}
        >
          {isAnalyzing ? 'Submitting...' : 'Submit'}
        </button>
      </div>

      <div
        className="editor-statusbar"
      >
        <span>Ln {lineCol.line}, Col {lineCol.col}</span>
        <span>{fileName}</span>
        <span style={{ marginLeft: 'auto' }}>UTF-8</span>
      </div>
    </div>
  )
}
