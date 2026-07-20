import { useState, useCallback, useMemo, useEffect, lazy, Suspense } from 'react'
import UrlInput from './components/UrlInput'
import VerdictDisplay from './components/VerdictDisplay'
import ConfidenceBar from './components/ConfidenceBar'
import RedFlags from './components/RedFlags'
import LanguageToggle from './components/LanguageToggle'

const SimilarNews = lazy(() => import('./components/SimilarNews'))

type Lang = 'es' | 'en'

interface Analysis {
  verdict: string
  confidence_score: number
  summary: string
  extracted_claims?: string[]
  reasoning: string[]
  red_flags: string[]
  positive_signals: string[]
  article_type?: string
  is_scam?: boolean
}

interface NewsItem {
  title: string
  url: string
  published: string
  source: string
}

interface ApiResponse {
  analysis: Analysis | null
  similar_news: NewsItem[]
  url_analyzed: string
  article_text: string
  domain: string
  is_credible_source: boolean
  error: string | null
}

const TRANSLATIONS = {
  es: {
    subtitle: 'Analizador de Credibilidad',
    summary: 'Resumen del Artículo',
    claims: 'Afirmaciones Principales',
    reasoning: 'Análisis Detallado',
    urlAnalyzed: 'URL Analizada',
    errorTitle: 'Error de Análisis',
    inputTitle: 'Verificar URL',
    connError: 'No se pudo conectar con el servidor. ¿Está corriendo el backend en el puerto 5001?',
    timeoutError: 'El análisis tardó demasiado. Intenta de nuevo.',
    credibleBadge: 'Fuente Verificada',
    articlePreview: 'Texto Extraído del Artículo',
    articleType: 'Tipo de Artículo',
    scamAlert: '¡ALERTA DE ESTAFA!',
    type_informativa: 'Informativa',
    type_comercial: 'Comercial',
    type_opinion: 'Opinión',
    type_clickbait: 'Clickbait',
    type_denuncia: 'Denuncia',
  },
  en: {
    subtitle: 'Credibility Analyzer',
    summary: 'Article Summary',
    claims: 'Main Claims',
    reasoning: 'Detailed Analysis',
    urlAnalyzed: 'Analyzed URL',
    errorTitle: 'Analysis Error',
    inputTitle: 'Verify URL',
    connError: 'Could not connect to server. Is the backend running on port 5001?',
    timeoutError: 'Analysis timed out. Please try again.',
    credibleBadge: 'Verified Source',
    articlePreview: 'Extracted Article Text',
    articleType: 'Article Type',
    scamAlert: 'SCAM ALERT!',
    type_informativa: 'Informative',
    type_comercial: 'Commercial',
    type_opinion: 'Opinion',
    type_clickbait: 'Clickbait',
    type_denuncia: 'Exposé',
  },
}

const URL_BAR_STYLE = {
  padding: '0.5rem 1rem',
  background: 'rgba(0,0,0,0.3)',
  border: '1px solid #1a1f2e',
  display: 'flex',
  alignItems: 'center',
  gap: '0.5rem',
  flexWrap: 'wrap' as const,
}

const ERROR_BOX_STYLE = {
  padding: '1rem 1.25rem',
  background: 'rgba(255,0,60,0.08)',
  border: '1px solid rgba(255,0,60,0.4)',
  clipPath: 'polygon(12px 0%, 100% 0%, calc(100% - 12px) 100%, 0% 100%)',
}

const DIVIDER_STYLE = {
  height: '1px',
  background: 'linear-gradient(90deg, transparent, #1a1f2e, transparent)',
  marginBottom: '1.5rem',
}

const FOOTER_STYLE = {
  marginTop: '3rem',
  textAlign: 'center' as const,
  paddingBottom: '1.5rem',
}

const RESULTS_COL_STYLE = {
  display: 'flex',
  flexDirection: 'column' as const,
  gap: '1rem',
}

const TYPE_STYLES: Record<string, { color: string; border: string; bg: string }> = {
  informativa: { color: '#00ff88', border: '#00ff88', bg: 'rgba(0,255,136,0.08)' },
  comercial: { color: '#ffaa00', border: '#ffaa00', bg: 'rgba(255,170,0,0.08)' },
  opinion: { color: '#00f0ff', border: '#00f0ff', bg: 'rgba(0,240,255,0.08)' },
  clickbait: { color: '#ff003c', border: '#ff003c', bg: 'rgba(255,0,60,0.08)' },
  denuncia: { color: '#ff44ff', border: '#ff44ff', bg: 'rgba(255,68,255,0.08)' },
}

const BADGE_STYLE: React.CSSProperties = {
  fontFamily: 'Share Tech Mono, monospace',
  fontSize: '0.65rem',
  letterSpacing: '0.15em',
  padding: '0.2rem 0.6rem',
  clipPath: 'polygon(4px 0%, 100% 0%, calc(100% - 4px) 100%, 0% 100%)',
}

export default function App() {
  const [lang, setLang] = useState<Lang>('es')
  const [loading, setLoading] = useState(false)
  const [translating, setTranslating] = useState(false)
  const [result, setResult] = useState<ApiResponse | null>(null)
  const [translatedResult, setTranslatedResult] = useState<ApiResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const tx = TRANSLATIONS[lang]

  const handleToggleLang = useCallback(() => {
    const nextLang = lang === 'es' ? 'en' : 'es'
    setLang(nextLang)
  }, [lang])

  useEffect(() => {
    if (lang === 'en' && result?.analysis && !translatedResult) {
      setTranslating(true)
      fetch('/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis: result.analysis, lang: 'en' }),
      })
        .then(r => r.json())
        .then(data => {
          if (data.translated) {
            setTranslatedResult({ ...result, analysis: data.translated })
          }
        })
        .catch(() => {})
        .finally(() => setTranslating(false))
    }
  }, [lang, result, translatedResult])

  const handleClear = useCallback(() => {
    setResult(null)
    setTranslatedResult(null)
    setError(null)
  }, [])

  const handleAnalyze = useCallback(async (url: string) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setTranslatedResult(null)

    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 60000)

    try {
      const res = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
        signal: controller.signal,
      })
      clearTimeout(timeout)
      const data: ApiResponse = await res.json()

      if (!res.ok || data.error) {
        setError(data.error ?? (lang === 'es' ? 'Error desconocido.' : 'Unknown error.'))
      } else {
        setResult(data)
      }
    } catch (e: unknown) {
      clearTimeout(timeout)
      if (e instanceof Error && e.name === 'AbortError') {
        setError(tx.timeoutError)
      } else {
        setError(tx.connError)
      }
    } finally {
      setLoading(false)
    }
  }, [lang, tx])

  const analysis = (lang === 'en' && translatedResult?.analysis) || result?.analysis ?? null

  const adjustedVerdict = useMemo(() => {
    if (!analysis) return null
    const score = analysis.confidence_score
    const isSocialMedia = result?.domain && (
      result.domain.includes('instagram.com') ||
      result.domain.includes('threads.net') ||
      result.domain.includes('threads.com') ||
      result.domain.includes('x.com') ||
      result.domain.includes('twitter.com') ||
      result.domain.includes('tiktok.com') ||
      result.domain.includes('facebook.com')
    )
    if (isSocialMedia) return analysis.verdict
    if (score < 50) return 'FALSO'
    if (score <= 69) return 'DUDOSO'
    return analysis.verdict
  }, [analysis, result])

  return (
    <div style={{ position: 'relative', minHeight: '100vh', width: '100%' }}>
      <div className="grid-bg" />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: '1400px', width: '100%', margin: '0 auto', padding: '1.5rem' }}>

        <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div>
            <h1 className="glitch" data-text="VERIFEX">VERIFEX</h1>
            <p style={{ color: '#3a5a6a', fontSize: '0.75rem', fontFamily: 'Share Tech Mono, monospace', letterSpacing: '0.2em', marginTop: '0.25rem' }}>
              {tx.subtitle}
            </p>
          </div>
          <LanguageToggle lang={lang} onToggle={handleToggleLang} />
        </header>

        <div className="main-grid">
          <div className="panel">
            <p className="label" style={{ marginBottom: '1rem' }}>{tx.inputTitle}</p>
            <UrlInput lang={lang} loading={loading} onAnalyze={handleAnalyze} onClear={handleClear} />
          </div>

          <div style={RESULTS_COL_STYLE}>
            {error && (
              <div style={ERROR_BOX_STYLE}>
                <p className="label" style={{ color: '#ff003c', marginBottom: '0.4rem' }}>{tx.errorTitle}</p>
                <p style={{ color: '#ff6b8a', fontSize: '1rem', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>{error}</p>
              </div>
            )}

            {analysis && result && (
              <>
                {/* URL + credible source badge */}
                <div style={URL_BAR_STYLE}>
                  <span className="label" style={{ display: 'inline', flexShrink: 0 }}>{tx.urlAnalyzed}:</span>
                  <span style={{ fontFamily: 'Share Tech Mono, monospace', fontSize: '0.72rem', color: '#3a5a6a', wordBreak: 'break-all', flex: 1 }}>
                    {result.url_analyzed}
                  </span>
                  {result.is_credible_source && (
                    <span style={{
                      fontFamily: 'Orbitron, monospace',
                      fontSize: '0.55rem',
                      letterSpacing: '0.15em',
                      color: '#00ff88',
                      border: '1px solid #00ff88',
                      padding: '0.15rem 0.5rem',
                      flexShrink: 0,
                      clipPath: 'polygon(4px 0%, 100% 0%, calc(100% - 4px) 100%, 0% 100%)',
                    }}>
                      ✓ {tx.credibleBadge}
                    </span>
                  )}
                </div>

                <VerdictDisplay verdict={adjustedVerdict ?? analysis.verdict} originalVerdict={analysis.verdict} lang={lang} />

                <ConfidenceBar score={analysis.confidence_score} lang={lang} />

                {/* Article type + scam alert */}
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                  {analysis.article_type && TYPE_STYLES[analysis.article_type] && (
                    <div style={{
                      ...BADGE_STYLE,
                      color: TYPE_STYLES[analysis.article_type].color,
                      border: `1px solid ${TYPE_STYLES[analysis.article_type].border}`,
                      background: TYPE_STYLES[analysis.article_type].bg,
                    }}>
                      {tx.articleType}: {tx[`type_${analysis.article_type}` as keyof typeof tx] || analysis.article_type}
                    </div>
                  )}
                  {analysis.is_scam && (
                    <div style={{
                      ...BADGE_STYLE,
                      color: '#ff003c',
                      border: '1px solid #ff003c',
                      background: 'rgba(255,0,60,0.12)',
                      animation: 'pulse 1.5s ease-in-out infinite',
                    }}>
                      ⚠ {tx.scamAlert}
                    </div>
                  )}
                </div>

                <div className="panel">
                  <p className="label" style={{ marginBottom: '0.6rem' }}>{tx.summary}</p>
                  <p style={{ color: '#c8d6e5', lineHeight: 1.75, fontSize: '1rem' }}>{analysis.summary}</p>
                </div>

                {/* Extracted claims */}
                {analysis.extracted_claims && analysis.extracted_claims.length > 0 && (
                  <div className="panel">
                    <p className="label" style={{ marginBottom: '0.75rem' }}>{tx.claims}</p>
                    <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {analysis.extracted_claims.map((c, i) => (
                        <li key={i} style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', fontSize: '1rem', color: '#a8b8c8', lineHeight: 1.5 }}>
                          <span style={{ color: '#ffaa00', fontFamily: 'Share Tech Mono', flexShrink: 0 }}>◆</span>
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {analysis.reasoning?.length > 0 && (
                  <div className="panel">
                    <p className="label" style={{ marginBottom: '0.75rem' }}>{tx.reasoning}</p>
                    <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {analysis.reasoning.map((r, i) => (
                        <li key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', fontSize: '1rem', color: '#a8b8c8', lineHeight: 1.6 }}>
                          <span style={{ color: '#00f0ff', fontFamily: 'Share Tech Mono', flexShrink: 0 }}>
                            {String(i + 1).padStart(2, '0')}
                          </span>
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <RedFlags
                  redFlags={analysis.red_flags ?? []}
                  positiveSignals={analysis.positive_signals ?? []}
                  lang={lang}
                />

                {/* Article text preview */}
                <div className="panel">
                  <p className="label" style={{ marginBottom: '0.75rem' }}>{tx.articlePreview}</p>
                  {result.article_text ? (
                    <p style={{
                      color: '#4a6a7a',
                      fontSize: '0.85rem',
                      lineHeight: 1.7,
                      fontFamily: 'Rajdhani, sans-serif',
                      maxHeight: '200px',
                      overflowY: 'auto',
                      borderLeft: '2px solid #1a1f2e',
                      paddingLeft: '0.75rem',
                    }}>
                      {result.article_text}
                    </p>
                  ) : (
                    <p style={{ color: '#3a5a6a', fontSize: '0.85rem', fontStyle: 'italic' }}>
                      —
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
        </div>

        {result?.similar_news && result.similar_news.length > 0 && (
          <div style={{ marginTop: '2rem' }}>
            <div style={DIVIDER_STYLE} />
            <Suspense fallback={null}>
              <SimilarNews news={result.similar_news} lang={lang} />
            </Suspense>
          </div>
        )}

        <footer style={FOOTER_STYLE}>
          <p style={{ fontFamily: 'Share Tech Mono, monospace', fontSize: '0.7rem', color: '#1a2a3a', letterSpacing: '0.2em' }}>
            VERIFEX v1.0 — POWERED BY GROQ API
          </p>
        </footer>
      </div>
    </div>
  )
}
