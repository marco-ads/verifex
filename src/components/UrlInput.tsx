import { useState, useCallback, memo } from 'react'

interface Props {
  lang: 'es' | 'en'
  loading: boolean
  onAnalyze: (url: string) => void
  onClear?: () => void
}

const TRANSLATIONS = {
  es: {
    placeholder: 'Ingresa una URL para analizar...',
    button: 'Analizar',
    analyzing: 'Analizando...',
    hint: 'Pega cualquier URL de noticia o página web',
    processing: 'Procesando señal',
  },
  en: {
    placeholder: 'Enter a URL to analyze...',
    button: 'Analyze',
    analyzing: 'Analyzing...',
    hint: 'Paste any news article or web page URL',
    processing: 'Processing signal',
  },
}

const HINT_STYLE = {
  color: '#3a5a6a',
  fontSize: '0.875rem',
  fontFamily: 'Share Tech Mono, monospace',
}

const SEG_INDICES = Array.from({ length: 10 }, (_, i) => i)

const LoadingSegments = memo(function LoadingSegments() {
  return (
    <div className="seg-bar">
      {SEG_INDICES.map(i => (
        <div key={i} className="seg active" style={{ animationDelay: `${i * 0.07}s` }} />
      ))}
    </div>
  )
})

const UrlInput = memo(function UrlInput({ lang, loading, onAnalyze, onClear }: Props) {
  const [url, setUrl] = useState('')
  const tx = TRANSLATIONS[lang]

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value)
  }, [])

  const handleClear = useCallback(() => {
    setUrl('')
    onClear?.()
  }, [onClear])

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim() && !loading) onAnalyze(url.trim())
  }, [url, loading, onAnalyze])

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      <div style={{ position: 'relative' }}>
        <input
          className="cyber-input"
          type="url"
          value={url}
          onChange={handleChange}
          placeholder={tx.placeholder}
          disabled={loading}
          required
          style={{ paddingRight: url ? '2.5rem' : '1rem' }}
        />
        {url && !loading && (
          <button
            type="button"
            onClick={handleClear}
            style={{
              position: 'absolute',
              right: '0.75rem',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              color: '#3a5a6a',
              cursor: 'pointer',
              fontSize: '1rem',
              lineHeight: 1,
              padding: '0.2rem',
              transition: 'color 0.2s',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = '#ff003c')}
            onMouseLeave={e => (e.currentTarget.style.color = '#3a5a6a')}
            title="Borrar"
          >
            ✕
          </button>
        )}
      </div>

      <p style={HINT_STYLE}>{tx.hint}</p>

      <button type="submit" className="cyber-btn" disabled={loading || !url.trim()}>
        {loading ? tx.analyzing : tx.button}
      </button>

      {loading && (
        <div style={{ marginTop: '0.5rem' }}>
          <p className="label" style={{ marginBottom: '0.5rem' }}>{tx.processing}</p>
          <LoadingSegments />
        </div>
      )}
    </form>
  )
})

export default UrlInput
