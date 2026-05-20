import { memo } from 'react'

interface Props {
  redFlags: string[]
  positiveSignals: string[]
  lang: 'es' | 'en'
}

const EMPTY_STYLE = { color: '#3a5a6a', fontSize: '0.875rem' }
const WRAP_STYLE = { display: 'flex', flexWrap: 'wrap' as const, gap: '0.5rem' }

const RedFlags = memo(function RedFlags({ redFlags, positiveSignals, lang }: Props) {
  return (
    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
      <div className="panel" style={{ flex: '1 1 200px' }}>
        <p className="label" style={{ marginBottom: '0.75rem' }}>
          {lang === 'es' ? 'Alertas Detectadas' : 'Detected Alerts'}
        </p>
        {redFlags.length === 0 ? (
          <p style={EMPTY_STYLE}>—</p>
        ) : (
          <div style={WRAP_STYLE}>
            {redFlags.map((flag, i) => (
              <span key={i} className="pill pill-red">⚠ {flag}</span>
            ))}
          </div>
        )}
      </div>
      <div className="panel" style={{ flex: '1 1 200px' }}>
        <p className="label" style={{ marginBottom: '0.75rem' }}>
          {lang === 'es' ? 'Señales Positivas' : 'Positive Signals'}
        </p>
        {positiveSignals.length === 0 ? (
          <p style={EMPTY_STYLE}>—</p>
        ) : (
          <div style={WRAP_STYLE}>
            {positiveSignals.map((sig, i) => (
              <span key={i} className="pill pill-cyan">✓ {sig}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
})

export default RedFlags
