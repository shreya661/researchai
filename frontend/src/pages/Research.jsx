import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import AgentTracker from '../components/AgentTracker'
import ReportViewer from '../components/ReportViewer'
import CitationList from '../components/CitationList'

export default function ResearchPage({ session, apiBase, onUpdate }) {
  const [sessionData, setSessionData] = useState(null)
  const [logs, setLogs] = useState([])
  const wsRef = useRef(null)
  const logStreamRef = useRef(null)

  useEffect(() => {
    loadSession()
    connectWebSocket()
    return () => wsRef.current?.close()
  }, [session.session_id])

  useEffect(() => {
    if (logStreamRef.current) {
      logStreamRef.current.scrollTop = logStreamRef.current.scrollHeight
    }
  }, [logs])

  const loadSession = async () => {
    try {
      const res = await axios.get(`${apiBase}/api/research/${session.session_id}/status`)
      setSessionData(res.data)
      onUpdate(res.data)
    } catch (e) {
      console.error('Failed to load session', e)
    }
  }

  const connectWebSocket = () => {
    if (wsRef.current) wsRef.current.close()
    const wsUrl = apiBase ? apiBase.replace(/^http/, 'ws') : 'ws://localhost:8000'
    const ws = new WebSocket(`${wsUrl}/api/research/ws/${session.session_id}`)
    wsRef.current = ws

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setLogs(prev => [...prev.slice(-50), { ...data, time: new Date().toLocaleTimeString() }])

      if (data.status === 'done' || data.status === 'error') {
        // Reload full session when done
        setTimeout(loadSession, 500)
      } else {
        setSessionData(prev => prev ? { ...prev, current_agent: data.agent } : prev)
      }
    }

    ws.onerror = () => addLog('system', '⚠ WebSocket connection error')
    ws.onclose = () => addLog('system', '● Connection closed')
  }

  const addLog = (agent, message) => {
    setLogs(prev => [...prev.slice(-50), { agent, message, time: new Date().toLocaleTimeString() }])
  }

  const handleDownloadPdf = () => {
    window.open(`${apiBase}/api/research/${session.session_id}/pdf`, '_blank')
  }

  const handleDownloadMd = () => {
    if (!sessionData?.report_markdown) return
    const blob = new Blob([sessionData.report_markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${session.topic.slice(0, 30).replace(/\s+/g, '_')}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const status = sessionData?.status || session.status
  const isDone = status === 'done'
  const isError = status === 'error'

  return (
    <div className="research-page">
      {/* Left Panel — Agent Progress */}
      <div className="research-left">
        {/* Topic Header */}
        <div className="topic-header">
          <div className="topic-label">Research Topic</div>
          <div className="topic-text">{session.topic}</div>
          <div className={`domain-badge-indicator ${sessionData?.domain || session.domain || 'general'}`}>
            {(() => {
              const dom = sessionData?.domain || session.domain || 'general';
              return dom === 'healthcare' ? '⚕️ Healthcare & Medicine' :
                     dom === 'education' ? '🎓 Education & Learning' :
                     dom === 'policy' ? '🏛️ Public Policy & Climate' :
                     dom === 'science' ? '🧪 Science & Tech' :
                     '🌐 General Research';
            })()}
          </div>
          <div className={`topic-status ${status}`}>
            {status === 'running' && <><span className="spinner" style={{ width: 10, height: 10, borderWidth: 1.5 }} /> Researching...</>}
            {status === 'done' && <>✓ Complete</>}
            {status === 'error' && <>✕ Error</>}
            {status === 'pending' && <>⏳ Pending</>}
          </div>
        </div>

        {/* Agent Steps */}
        <AgentTracker
          currentAgent={sessionData?.current_agent || 'search'}
          status={status}
        />

        {/* Log Stream */}
        <div className="log-stream" id="log-stream" ref={logStreamRef}>
          {logs.length === 0 && (
            <div className="log-line" style={{ color: 'var(--text-muted)' }}>
              Waiting for agent updates...
            </div>
          )}
          {logs.map((log, i) => (
            <div
              key={i}
              className={`log-line ${i === logs.length - 1 ? 'active' : ''}`}
            >
              [{log.time}] {log.message}
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel — Report */}
      <div className="research-right">
        {isDone && (
          <div className="download-bar">
            <button id="download-pdf-btn" className="download-btn primary" onClick={handleDownloadPdf}>
              ⬇ Download PDF
            </button>
            <button id="download-md-btn" className="download-btn secondary" onClick={handleDownloadMd}>
              ⬇ Markdown
            </button>
          </div>
        )}

        <ReportViewer
          topic={session.topic}
          markdown={sessionData?.report_markdown}
          status={status}
          errorMessage={sessionData?.error_message}
        />

        {isDone && sessionData?.citations?.length > 0 && (
          <CitationList citations={sessionData.citations} />
        )}
      </div>
    </div>
  )
}
