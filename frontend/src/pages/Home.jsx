import { useState } from 'react'

const DOMAINS = [
  { id: 'general', label: 'General', icon: '🌐', desc: 'All-purpose research and web facts' },
  { id: 'healthcare', label: 'Healthcare & Medicine', icon: '⚕️', desc: 'Clinical trials, studies and evidence' },
  { id: 'education', label: 'Education & Learning', icon: '🎓', desc: 'Pedagogy, learning outcomes and school impacts' },
  { id: 'policy', label: 'Public Policy & Climate', icon: '🏛️', desc: 'Socioeconomic plans, laws and environment' },
  { id: 'science', label: 'Science & Tech', icon: '🧪', desc: 'Peer-reviewed details, tech and breakthroughs' }
]

const DOMAIN_EXAMPLES = {
  general: [
    'Climate change and renewable energy',
    'Quantum computing applications',
    'Mental health and social media',
    'SpaceX Mars mission progress'
  ],
  healthcare: [
    'Efficacy of telemedicine vs in-person care',
    'CRISPR gene editing in sickle cell therapy',
    'AI models for early breast cancer detection',
    'Intermittent fasting impact on cardiovascular health'
  ],
  education: [
    'Impact of classroom gamification on math scores',
    'Efficacy of bilingual immersion education models',
    'Role of active recall in long-term learning retention',
    'Project-based learning vs standardized test readiness'
  ],
  policy: [
    'Socioeconomic impact of universal basic income trials',
    'Carbon tax policies and greenhouse gas reduction',
    'Efficacy of zoning reforms on housing affordability',
    'Soda tax outcomes on public health indices'
  ],
  science: [
    'Recent breakthroughs in room-temperature superconductors',
    'Solid-state batteries vs lithium-ion performance',
    'Mars terraforming feasibility and soil composition',
    'Perovskite solar cell efficiency improvements'
  ]
}

const AGENT_FLOW = [
  { icon: '🔍', label: 'Search' },
  { icon: '📖', label: 'Research' },
  { icon: '✅', label: 'Fact-Check' },
  { icon: '📝', label: 'Report' },
]

export default function HomePage({ onSearch }) {
  const [topic, setTopic] = useState('')
  const [domain, setDomain] = useState('general')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!topic.trim() || loading) return
    setLoading(true)
    await onSearch(topic.trim(), domain)
    setLoading(false)
  }

  const examples = DOMAIN_EXAMPLES[domain] || DOMAIN_EXAMPLES.general

  return (
    <div className="home-page">
      {/* Background orbs */}
      <div className="home-bg-orb orb1" />
      <div className="home-bg-orb orb2" />

      <div className="home-hero fade-in">
        {/* Badge */}
        <div className="hero-badge">
          <span>●</span> Agents for Good Initiative
        </div>

        {/* Title */}
        <h1 className="home-title">
          Research anything with<br />
          <span className="gradient-text">AI Agents</span>
        </h1>

        {/* Subtitle */}
        <p className="home-subtitle">
          Select a research domain and enter your question. Our multi-agent system will search the web,
          verify facts, and generate a citation-rich report.
        </p>

        {/* Domain Selector Grid */}
        <div className="domain-grid">
          {DOMAINS.map(d => (
            <button
              key={d.id}
              type="button"
              className={`domain-card ${domain === d.id ? 'active' : ''}`}
              onClick={() => !loading && setDomain(d.id)}
            >
              <span className="domain-card-icon">{d.icon}</span>
              <span className="domain-card-content">
                <span className="domain-card-label">{d.label}</span>
                <span className="domain-card-desc">{d.desc}</span>
              </span>
            </button>
          ))}
        </div>

        {/* Search */}
        <form className="search-container" onSubmit={handleSubmit}>
          <input
            id="research-topic-input"
            className="search-input"
            type="text"
            placeholder={
              domain === 'healthcare' ? 'e.g. mRNA vaccines long-term efficacy...' :
              domain === 'education' ? 'e.g. benefits of preschool education...' :
              domain === 'policy' ? 'e.g. economic impact of green energy subsidies...' :
              domain === 'science' ? 'e.g. quantum cryptography security standard...' :
              'e.g. Impact of AI on job markets...'
            }
            value={topic}
            onChange={e => setTopic(e.target.value)}
            disabled={loading}
            autoFocus
          />
          <button
            id="start-research-btn"
            className="search-btn"
            type="submit"
            disabled={!topic.trim() || loading}
          >
            {loading ? <span className="spinner" /> : '→'}
            {loading ? 'Starting...' : 'Research'}
          </button>
        </form>

        {/* Dynamic Example topics */}
        <div className="example-topics">
          {examples.map(ex => (
            <button
              key={ex}
              type="button"
              className="example-chip"
              onClick={() => setTopic(ex)}
            >
              {ex}
            </button>
          ))}
        </div>

        {/* Agent flow preview */}
        <div className="agent-flow-preview">
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginRight: 4 }}>Your question</span>
          <span className="flow-arrow">→</span>
          {AGENT_FLOW.map((node, i) => (
            <div key={node.label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div className="flow-node">
                {node.icon} {node.label}
              </div>
              {i < AGENT_FLOW.length - 1 && <span className="flow-arrow">→</span>}
            </div>
          ))}
          <span className="flow-arrow">→</span>
          <span style={{ fontSize: '0.78rem', color: 'var(--accent-green)' }}>📄 Report</span>
        </div>
      </div>
    </div>
  )
}
