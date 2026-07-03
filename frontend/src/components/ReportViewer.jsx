import { useMemo } from 'react'

function parseMarkdown(md) {
  const lines = md.split('\n')
  const elements = []
  let key = 0

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) {
      elements.push(<br key={key++} />)
    } else if (trimmed.startsWith('## ')) {
      elements.push(<h2 key={key++}>{trimmed.slice(3)}</h2>)
    } else if (trimmed.startsWith('### ')) {
      elements.push(<h3 key={key++}>{trimmed.slice(4)}</h3>)
    } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      elements.push(<li key={key++} dangerouslySetInnerHTML={{ __html: inlineParse(trimmed.slice(2)) }} />)
    } else {
      elements.push(<p key={key++} dangerouslySetInnerHTML={{ __html: inlineParse(trimmed) }} />)
    }
  }
  return elements
}

function inlineParse(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\[(\d+)\]/g, '<sup style="color:var(--primary-light);font-size:0.75em">[$1]</sup>')
}

export default function ReportViewer({ topic, markdown, status, errorMessage }) {
  const parsed = useMemo(() => markdown ? parseMarkdown(markdown) : null, [markdown])

  if (status === 'error') {
    return (
      <div className="report-viewer">
        <div className="report-empty">
          <span style={{ fontSize: '2rem' }}>⚠️</span>
          <span style={{ color: 'var(--accent)' }}>Research failed</span>
          <span style={{ fontSize: '0.82rem', maxWidth: 400, textAlign: 'center' }}>
            {errorMessage || 'An unexpected error occurred. Please try again.'}
          </span>
        </div>
      </div>
    )
  }

  if (!markdown) {
    return (
      <div className="report-viewer">
        <div className="report-empty">
          <span style={{ fontSize: '2.5rem' }}>🔬</span>
          <span>Your report will appear here once research is complete.</span>
          {status === 'running' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent-yellow)', fontSize: '0.85rem' }}>
              <span className="spinner" style={{ width: 14, height: 14, borderColor: 'rgba(255,209,102,0.3)', borderTopColor: 'var(--accent-yellow)' }} />
              Agents are working...
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="report-viewer fade-in">
      <div className="report-title">Research Report</div>
      <div className="report-topic">Topic: {topic}</div>
      <div className="report-body">
        {parsed}
      </div>
    </div>
  )
}
