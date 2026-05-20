import { memo } from 'react'

interface NewsItem {
  title: string
  url: string
  published: string
  source: string
}

interface Props {
  news: NewsItem[]
  lang: 'es' | 'en'
}

const GRID_STYLE = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
  gap: '0.75rem',
}

const SOURCE_STYLE = {
  color: '#00f0ff',
  fontSize: '0.7rem',
  fontFamily: 'Orbitron, monospace',
  marginBottom: '0.5rem',
  letterSpacing: '0.1em',
  display: 'block',
}

const TITLE_STYLE = {
  color: '#c8d6e5',
  fontSize: '1rem',
  lineHeight: 1.45,
  marginBottom: '0.5rem',
}

const DATE_STYLE = {
  color: '#3a5a6a',
  fontSize: '0.75rem',
  fontFamily: 'Share Tech Mono, monospace',
}

function formatDate(raw: string) {
  try {
    return new Date(raw).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch {
    return raw
  }
}

const SimilarNews = memo(function SimilarNews({ news, lang }: Props) {
  if (!news || news.length === 0) return null

  return (
    <div>
      <p className="label" style={{ marginBottom: '1rem' }}>
        {lang === 'es' ? 'Noticias Similares' : 'Similar News'}
      </p>
      <div style={GRID_STYLE}>
        {news.map((item, i) => (
          <a
            key={i}
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="news-card panel"
            style={{ textDecoration: 'none', display: 'block' }}
          >
            {item.source && <span style={SOURCE_STYLE}>{item.source}</span>}
            <p style={TITLE_STYLE}>{item.title}</p>
            {item.published && <p style={DATE_STYLE}>{formatDate(item.published)}</p>}
          </a>
        ))}
      </div>
    </div>
  )
})

export default SimilarNews
