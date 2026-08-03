import Editor from '@monaco-editor/react'

import { useTheme } from '../context/useTheme'
import { languageConfig } from '../data/languages'


const FILE_NAMES = {
  python: 'main.py',
  javascript: 'main.js',
  java: 'Main.java',
  cpp: 'main.cpp',
}


export default function CodeEditorPanel({
  code,
  language,
  selectedCaseNumber,
  busyAction,
  onCodeChange,
  onRun,
  onSubmit,
}) {
  const { theme } = useTheme()
  const config = languageConfig[language] || languageConfig.python
  const disabled = !code.trim() || Boolean(busyAction)

  return (
    <section className="editor-panel" aria-label="Code editor">
      <header className="editor-header">
        <div className="file-name">
          <span className="file-language">{config.icon}</span>
          <strong>{FILE_NAMES[language] || 'main.txt'}</strong>
        </div>
        <span className="entry-contract">stdin / stdout</span>
      </header>

      <div className="editor-canvas">
        <Editor
          height="100%"
          language={config.monacoLang}
          value={code}
          theme={theme === 'dark' ? 'vs-dark' : 'light'}
          onChange={(value) => onCodeChange(value || '')}
          onMount={(editor) => editor.focus()}
          loading={<div className="page-state">Loading editor...</div>}
          options={{
            automaticLayout: true,
            minimap: { enabled: false },
            fontFamily: 'Consolas, "Courier New", monospace',
            fontSize: 14,
            lineHeight: 22,
            lineNumbersMinChars: 3,
            padding: { top: 14, bottom: 14 },
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            tabSize: 4,
            insertSpaces: true,
            wordWrap: 'on',
            renderLineHighlight: 'line',
            bracketPairColorization: { enabled: true },
          }}
        />
      </div>

      <footer className="editor-toolbar">
        <span className="editor-status">{code.trim() ? 'Ready' : 'Add your solution to continue'}</span>
        <div className="editor-actions">
          <button className="button button-secondary" disabled={disabled} type="button" onClick={onRun}>
            {busyAction === 'run' ? 'Running' : `Run case ${selectedCaseNumber || 1}`}
          </button>
          <button className="button button-primary" disabled={disabled} type="button" onClick={onSubmit}>
            {busyAction === 'submit' ? 'Submitting' : 'Submit'}
          </button>
        </div>
      </footer>
    </section>
  )
}
