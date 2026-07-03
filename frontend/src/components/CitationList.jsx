export default function CitationList({ citations }) {
  if (!citations || citations.length === 0) return null

  return (
    <div className="citations-panel fade-in">
      <div className="citations-title">📚 References ({citations.length})</div>
      {citations.map((c, i) => (
        <div key={i} className="citation-item">
          <div className="citation-num">[{i + 1}]</div>
          <div className="citation-content">
            <div className="citation-title-text">{c.title || 'Untitled'}</div>
            <a
              className="citation-url"
              href={c.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              {c.url}
            </a>
            {c.snippet && (
              <div className="citation-snippet">
                {c.snippet.slice(0, 180)}{c.snippet.length > 180 ? '...' : ''}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
