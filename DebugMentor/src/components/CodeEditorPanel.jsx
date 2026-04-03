import { useRef, useState, useCallback } from 'react'
import MonacoEditor from '@monaco-editor/react'
import { languageConfig } from '../data/mockData'
import { useTheme } from '../context/ThemeContext'

// ─── Monaco dark theme ────────────────────────────────────────────────────────
const MONACO_DARK = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment',    foreground: '4A5568', fontStyle: 'italic' },
    { token: 'keyword',    foreground: 'BB86FC', fontStyle: 'bold' },
    { token: 'string',     foreground: 'A8FF78' },
    { token: 'number',     foreground: 'FFB347' },
    { token: 'type',       foreground: '4FFFB0' },
    { token: 'function',   foreground: '79D6F9' },
    { token: 'identifier', foreground: 'E8EAF0' },
    { token: 'delimiter',  foreground: '7A8099' },
  ],
  colors: {
    'editor.background':               '#13161E',
    'editor.foreground':               '#E8EAF0',
    'editor.lineHighlightBackground':  '#1F2430',
    'editor.selectionBackground':      '#4FFFB025',
    'editorLineNumber.foreground':     '#3A4055',
    'editorLineNumber.activeForeground': '#7A8099',
    'editorCursor.foreground':         '#4FFFB0',
    'editorIndentGuide.background1':    '#1F2430',
    'editorIndentGuide.activeBackground1': '#2A3045',
    'scrollbar.shadow':                '#00000000',
    'scrollbarSlider.background':      '#1F243060',
    'scrollbarSlider.hoverBackground': '#2A304580',
  }
}

// ─── Monaco light theme ───────────────────────────────────────────────────────
const MONACO_LIGHT = {
  base: 'vs',
  inherit: true,
  rules: [
    { token: 'comment',    foreground: '8896B0', fontStyle: 'italic' },
    { token: 'keyword',    foreground: '7C4DFF', fontStyle: 'bold' },
    { token: 'string',     foreground: '1B7A3E' },
    { token: 'number',     foreground: 'D4620A' },
    { token: 'type',       foreground: '007A50' },
    { token: 'function',   foreground: '1565C0' },
    { token: 'identifier', foreground: '1A1D23' },
    { token: 'delimiter',  foreground: '5A6070' },
  ],
  colors: {
    'editor.background':               '#FFFFFF',
    'editor.foreground':               '#1A1D23',
    'editor.lineHighlightBackground':  '#F0F2F7',
    'editor.selectionBackground':      '#4FFFB030',
    'editorLineNumber.foreground':     '#C8CEDF',
    'editorLineNumber.activeForeground': '#5A6070',
    'editorCursor.foreground':         '#00875A',
    'editorIndentGuide.background1':    '#E0E4EF',
    'editorIndentGuide.activeBackground1': '#BCC3D8',
    'scrollbar.shadow':                '#00000000',
    'scrollbarSlider.background':      '#DDE1EF60',
    'scrollbarSlider.hoverBackground': '#BCC3D880',
  }
}

const fileNames = {
  python: 'solution.py',
  cpp: 'solution.cpp',
  java: 'Solution.java',
  javascript: 'solution.js'
}

export default function CodeEditorPanel({
  code,           // display code (focused or complete)
  language,
  editorMode,     // 'focused' | 'complete'
  isAnalyzing,
  isRunning,
  onCodeChange,
  onRun,
  onSubmit,
}) {
  const editorRef  = useRef(null)
  const monacoRef  = useRef(null)
  const [lineCol, setLineCol] = useState({ line: 1, col: 1 })
  const { theme } = useTheme()
  const cfg        = languageConfig[language]
  const fileName   = fileNames[language] || 'solution.py'

  // ─── Apply correct Monaco theme whenever app theme changes ────────────────
  const handleEditorMount = useCallback((editor, monaco) => {
    editorRef.current  = editor
    monacoRef.current  = monaco

    monaco.editor.defineTheme('debugmentor-dark',  MONACO_DARK)
    monaco.editor.defineTheme('debugmentor-light', MONACO_LIGHT)
    monaco.editor.setTheme(theme === 'light' ? 'debugmentor-light' : 'debugmentor-dark')

    editor.onDidChangeCursorPosition(e => {
      setLineCol({ line: e.position.lineNumber, col: e.position.column })
    })
  }, [theme])

  // Update Monaco theme when toggled (without remounting editor)
  const monacoTheme = theme === 'light' ? 'debugmentor-light' : 'debugmentor-dark'

  return (
    <div className="editor-panel" style={{ width: '60%' }}>

      {/* ── File Tab Bar ─────────────────────────────────────── */}
      <div className="file-tabbar">
        <div className="file-tab active">
          <span className="file-tab-dot" style={{ background: 'var(--accent-danger)' }} />
          {fileName}
        </div>
        <div className="file-tab">
          <span className="file-tab-dot" style={{ background: 'var(--accent-primary)' }} />
          test_runner.py
        </div>
        <div className="file-tab">
          <span className="file-tab-dot" style={{ background: 'var(--text-secondary)' }} />
          notes.md
        </div>
      </div>

      {/* ── Breadcrumb ───────────────────────────────────────── */}
      <div className="breadcrumb-bar">
        <span>src</span>
        <span className="crumb-sep">/</span>
        <span>problems</span>
        <span className="crumb-sep">/</span>
        <span className="crumb-file">{fileName}</span>
        <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{
            background: 'rgba(255,95,109,0.1)',
            border: '1px solid rgba(255,95,109,0.3)',
            borderRadius: 4,
            padding: '2px 8px',
            color: 'var(--accent-danger)',
            fontSize: 11,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 5
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-danger)', display: 'inline-block' }} />
            1 error detected
          </span>
        </span>
      </div>


      {/* ── Monaco Editor ────────────────────────────────────── */}
      <div className="editor-container">
        <MonacoEditor
          height="100%"
          language={cfg.monacoLang}
          value={code}
          theme={monacoTheme}
          onChange={v => onCodeChange(v || '')}
          onMount={handleEditorMount}
          options={{
            fontSize: 14,
            fontFamily: "'JetBrains Mono', 'Monaco', 'Courier New', monospace",
            fontLigatures: true,
            lineNumbers: 'on',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            readOnly: false,
            renderWhitespace: 'selection',
            smoothScrolling: true,
            cursorBlinking: 'phase',
            cursorSmoothCaretAnimation: 'on',
            padding: { top: 16, bottom: 16 },
            lineDecorationsWidth: 8,
            folding: true,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            wordWrap: 'off',
            renderLineHighlight: 'gutter',
            overviewRulerLanes: 0,
            hideCursorInOverviewRuler: true,
            scrollbar: {
              vertical: 'auto',
              horizontal: 'auto',
              verticalScrollbarSize: 6,
              horizontalScrollbarSize: 6,
            }
          }}
        />
      </div>

      {/* ── Editor Toolbar ───────────────────────────────────── */}
      <div className="editor-toolbar">
        {/* Language badge */}
        <div className="lang-badge">
          <span style={{
            width: 8, height: 8, borderRadius: '50%',
            background: 'var(--accent-primary)',
            display: 'inline-block',
            boxShadow: '0 0 6px var(--accent-primary)'
          }} />
          {cfg.label}
        </div>


        <button
          id="btn-run-code"
          className="btn-run"
          onClick={onRun}
          disabled={isRunning || isAnalyzing}
        >
          {isRunning ? (
            <><div className="spinner" style={{ borderTopColor: 'var(--accent-primary)', borderColor: 'rgba(79,255,176,0.3)' }} /> Running...</>
          ) : (
            <>▶ Run Code</>
          )}
        </button>

        <button
          id="btn-submit-analysis"
          className={`btn-submit ${!isAnalyzing ? 'btn-submit-pulse' : ''}`}
          onClick={onSubmit}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <><div className="spinner" /> Analyzing...</>
          ) : (
            <>⚡ Submit</>
          )}
        </button>


      </div>

      {/* ── Bottom meta bar ──────────────────────────────────── */}
      <div style={{
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
        color: 'var(--text-secondary)'
      }}>
        <span>⚡</span>
        <span>Ln {lineCol.line}, Col {lineCol.col}</span>
        <span style={{ color: 'var(--border-bright)' }}>·</span>
        <span style={{ color: 'var(--text-secondary)' }}>
          Standard Mode
        </span>
        <span style={{ marginLeft: 'auto' }}>UTF-8</span>
      </div>
    </div>
  )
}
