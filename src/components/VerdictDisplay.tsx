import { memo, useMemo } from 'react'

interface Props {
  verdict: string
  originalVerdict?: string
  lang: 'es' | 'en'
}

const VERDICT_CONFIG: Record<string, { color: string; border: string; subtitleEs: string; subtitleEn: string }> = {
  REAL: {
    color: '#00f0ff',
    border: 'rgba(0,240,255,0.3)',
    subtitleEs: 'El contenido parece ser información verificada y legítima.',
    subtitleEn: 'The content appears to be verified and legitimate information.',
  },
  FALSO: {
    color: '#ff003c',
    border: 'rgba(255,0,60,0.3)',
    subtitleEs: 'Se detectaron indicadores de información falsa o manipulada.',
    subtitleEn: 'Indicators of false or manipulated information were detected.',
  },
  'SÁTIRA': {
    color: '#ffaa00',
    border: 'rgba(255,170,0,0.3)',
    subtitleEs: 'El contenido tiene carácter satírico o de humor, no informativo.',
    subtitleEn: 'The content is satirical or humorous, not informative.',
  },
  ESTAFA: {
    color: '#b400ff',
    border: 'rgba(180,0,255,0.3)',
    subtitleEs: 'Se detectaron señales de contenido fraudulento o engañoso.',
    subtitleEn: 'Signals of fraudulent or deceptive content were detected.',
  },
  DUDOSO: {
    color: '#ffaa00',
    border: 'rgba(255,170,0,0.3)',
    subtitleEs: 'El contenido tiene señales mixtas y no se puede determinar su veracidad con certeza.',
    subtitleEn: 'The content has mixed signals and its veracity cannot be determined with certainty.',
  },
  'NO VERIFICABLE': {
    color: '#6b7280',
    border: 'rgba(107,114,128,0.3)',
    subtitleEs: 'No hay suficiente información para verificar este contenido.',
    subtitleEn: 'There is not enough information to verify this content.',
  },
}

const FALLBACK_CFG = VERDICT_CONFIG['NO VERIFICABLE']

const VerdictDisplay = memo(function VerdictDisplay({ verdict, originalVerdict, lang }: Props) {
  const cfg = VERDICT_CONFIG[verdict] ?? FALLBACK_CFG
  const adjusted = originalVerdict !== undefined && originalVerdict !== verdict

  const containerStyle = useMemo(() => ({
    background: cfg.border,
    border: `1px solid ${cfg.color}`,
    clipPath: 'polygon(12px 0%, 100% 0%, calc(100% - 12px) 100%, 0% 100%)',
    padding: '1.5rem',
    boxShadow: `0 0 30px ${cfg.border}`,
  }), [cfg])

  const wordStyle = useMemo(() => ({
    fontFamily: 'Orbitron, monospace',
    fontWeight: 900,
    fontSize: '2.5rem',
    color: cfg.color,
    textShadow: `0 0 20px ${cfg.color}`,
    letterSpacing: '0.08em',
  }), [cfg])

  return (
    <div style={containerStyle}>
      <div style={wordStyle}>{verdict}</div>
      {adjusted && (
        <p style={{ color: '#6b7280', marginTop: '0.2rem', fontFamily: 'Share Tech Mono, monospace', fontSize: '0.75rem', letterSpacing: '0.1em' }}>
          {lang === 'es' ? `IA clasificó como: ${originalVerdict}` : `AI classified as: ${originalVerdict}`}
        </p>
      )}
      <p style={{ color: '#8a9ab0', marginTop: '0.4rem', fontFamily: 'Rajdhani, sans-serif', fontSize: '1rem' }}>
        {lang === 'es' ? cfg.subtitleEs : cfg.subtitleEn}
      </p>
    </div>
  )
})

export default VerdictDisplay
