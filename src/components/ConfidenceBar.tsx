import { memo, useMemo } from 'react'

interface Props {
  score: number
  lang: 'es' | 'en'
}

const SEG_COLORS: Record<string, string> = {
  red: '#ff003c',
  orange: '#ffaa00',
  cyan: '#00f0ff',
  green: '#00ff88',
}

const LIT_CLASSES: Record<string, string> = {
  red: 'lit-red',
  orange: 'lit-orange',
  cyan: 'lit-cyan',
  green: 'lit-green',
}

function getColorKey(score: number): string {
  if (score <= 40) return 'red'
  if (score <= 69) return 'orange'
  if (score <= 89) return 'cyan'
  return 'green'
}

const SEG_INDICES = Array.from({ length: 20 }, (_, i) => i)

const ConfidenceBar = memo(function ConfidenceBar({ score, lang }: Props) {
  const colorKey = getColorKey(score)
  const segColor = SEG_COLORS[colorKey]
  const litClass = LIT_CLASSES[colorKey]
  const litCount = Math.round((score / 100) * 20)

  const scoreStyle = useMemo(() => ({
    fontSize: '2rem',
    color: segColor,
    textShadow: `0 0 15px ${segColor}`,
    marginBottom: '0.75rem',
  }), [segColor])

  return (
    <div className="panel">
      <p className="label" style={{ marginBottom: '0.75rem' }}>
        {lang === 'es' ? 'Índice de Confiabilidad' : 'Credibility Index'}
      </p>
      <div className="mono" style={scoreStyle}>
        {score} <span style={{ fontSize: '1rem', color: '#3a5a6a' }}>/ 100</span>
      </div>
      <div style={{ display: 'flex', gap: '3px' }}>
        {SEG_INDICES.map(i => (
          <div key={i} className={`conf-seg${i < litCount ? ` ${litClass}` : ''}`} />
        ))}
      </div>
    </div>
  )
})

export default ConfidenceBar
