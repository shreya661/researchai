import { useState, useEffect } from 'react'
import axios from 'axios'
import HomePage from './pages/Home'
import ResearchPage from './pages/Research'
import './index.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [currentSession, setCurrentSession] = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/history`)
      setHistory(res.data)
    } catch (e) {
      console.error('Failed to fetch history', e)
    }
  }

  const startResearch = async (topic, domain) => {
    try {
      const res = await axios.post(`${API_BASE}/api/research/start`, { topic, domain })
      const session = { session_id: res.data.session_id, topic, domain, status: 'running' }
      setCurrentSession(session)
      setHistory(prev => [{ ...session, created_at: new Date().toISOString() }, ...prev])
    } catch (e) {
      console.error('Failed to start research', e)
    }
  }

  const deleteSession = async (sessionId) => {
    try {
      await axios.delete(`${API_BASE}/api/history/${sessionId}`)
      setHistory(prev => prev.filter(h => h.session_id !== sessionId))
      if (currentSession?.session_id === sessionId) setCurrentSession(null)
    } catch (e) {
      console.error('Failed to delete', e)
    }
  }

  const onSessionUpdate = (updatedSession) => {
    setHistory(prev =>
      prev.map(h => h.session_id === updatedSession.session_id ? { ...h, ...updatedSession } : h)
    )
  }

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <a className="logo" href="#">
            <div className="logo-icon">🔬</div>
            <span className="logo-text">ResearchLab AI</span>
          </a>
          <div className="logo-sub">Multi-Agent Research System</div>
        </div>

        <div className="sidebar-section">
          <button className="new-research-btn" onClick={() => setCurrentSession(null)}>
            <span>＋</span> New Research
          </button>

          <div className="sidebar-label">Recent Research</div>
          {history.length === 0 && (
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', padding: '0 8px' }}>
              No research yet. Start your first query!
            </p>
          )}
          {history.map(item => (
            <div
              key={item.session_id}
              className={`history-item ${currentSession?.session_id === item.session_id ? 'active' : ''}`}
              onClick={() => setCurrentSession(item)}
            >
              <div className={`history-dot ${item.status}`} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span className="history-domain-icon" style={{ fontSize: '0.9rem' }}>
                    {item.domain === 'healthcare' ? '⚕️' :
                     item.domain === 'education' ? '🎓' :
                     item.domain === 'policy' ? '🏛️' :
                     item.domain === 'science' ? '🧪' : '🌐'}
                  </span>
                  <div className="history-topic">{item.topic}</div>
                </div>
                <div className="history-date">
                  {new Date(item.created_at).toLocaleDateString()}
                </div>
              </div>
              <button
                className="history-delete"
                onClick={e => { e.stopPropagation(); deleteSession(item.session_id) }}
                title="Delete"
              >✕</button>
            </div>
          ))}
        </div>
      </aside>

      {/* Main */}
      <main className="main-content">
        {currentSession ? (
          <ResearchPage
            session={currentSession}
            apiBase={API_BASE}
            onUpdate={onSessionUpdate}
          />
        ) : (
          <HomePage onSearch={startResearch} />
        )}
      </main>
    </div>
  )
}
