const AGENTS = [
  {
    key: 'search',
    name: 'Search Agent',
    icon: '🔍',
    color: 'var(--agent-search)',
    msg: 'Searching the web for relevant sources...',
    doneMsg: 'Found and collected web sources',
  },
  {
    key: 'research',
    name: 'Research Agent',
    icon: '📖',
    color: 'var(--agent-research)',
    msg: 'Reading and summarizing each source...',
    doneMsg: 'Summarized all sources',
  },
  {
    key: 'factcheck',
    name: 'Fact-Check Agent',
    icon: '✅',
    color: 'var(--agent-factcheck)',
    msg: 'Verifying facts across sources...',
    doneMsg: 'Facts verified and filtered',
  },
  {
    key: 'report',
    name: 'Report Agent',
    icon: '📝',
    color: 'var(--agent-report)',
    msg: 'Writing the final research report...',
    doneMsg: 'Report generated successfully',
  },
]

const AGENT_ORDER = ['search', 'research', 'factcheck', 'report', 'done']

function getAgentState(agentKey, currentAgent, overallStatus) {
  const currentIdx = AGENT_ORDER.indexOf(currentAgent)
  const agentIdx = AGENT_ORDER.indexOf(agentKey)

  if (overallStatus === 'done') return 'done'
  if (overallStatus === 'error' && agentIdx >= currentIdx) return 'waiting'
  if (agentIdx < currentIdx) return 'done'
  if (agentIdx === currentIdx) return 'active'
  return 'waiting'
}

export default function AgentTracker({ currentAgent, status }) {
  return (
    <div className="agent-tracker">
      {AGENTS.map(agent => {
        const state = getAgentState(agent.key, currentAgent, status)
        return (
          <div
            key={agent.key}
            id={`agent-step-${agent.key}`}
            className={`agent-step ${state}`}
          >
            <div
              className="agent-icon"
              style={{ background: state === 'waiting' ? 'var(--bg-elevated)' : `${agent.color}22`, border: `1px solid ${state === 'waiting' ? 'transparent' : agent.color}` }}
            >
              {agent.icon}
            </div>
            <div className="agent-info">
              <div className="agent-name">{agent.name}</div>
              <div className="agent-msg">
                {state === 'active' ? agent.msg : state === 'done' ? agent.doneMsg : 'Waiting...'}
              </div>
            </div>
            <div className="agent-status-icon">
              {state === 'done' && '✅'}
              {state === 'active' && <span className="spinner" style={{ width: 14, height: 14 }} />}
              {state === 'waiting' && '⏳'}
            </div>
          </div>
        )
      })}
    </div>
  )
}
