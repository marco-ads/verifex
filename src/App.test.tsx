import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

const mockApiResponse = {
  analysis: {
    verdict: 'REAL',
    confidence_score: 85,
    summary: 'This is a test summary.',
    reasoning: ['First reason', 'Second reason'],
    red_flags: [],
    positive_signals: ['Verified source'],
    article_type: 'informativa',
    is_scam: false,
    extracted_claims: ['Claim one', 'Claim two'],
  },
  similar_news: [
    { title: 'Related news', url: 'https://example.com/related', published: '2025-03-01', source: 'Other Source' },
  ],
  url_analyzed: 'https://example.com/test-article',
  article_text: 'Full article text here.',
  domain: 'example.com',
  is_credible_source: true,
  error: null,
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('App integration', () => {
  it('renders title and language toggle', () => {
    render(<App />)
    expect(screen.getByText('VERIFEX')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'EN' })).toBeInTheDocument()
  })

  it('toggles language', async () => {
    const user = userEvent.setup()
    render(<App />)

    expect(screen.getByText(/analizador de credibilidad/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'EN' }))
    expect(screen.getByText(/credibility analyzer/i)).toBeInTheDocument()
  })

  it('analyzes a URL and displays results', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockApiResponse),
    } as Response)

    const user = userEvent.setup()
    render(<App />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://example.com/test-article')

    const button = screen.getByRole('button', { name: /analizar/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('REAL')).toBeInTheDocument()
    })

    expect(screen.getByText('85')).toBeInTheDocument()
    expect(screen.getByText(/test summary/i)).toBeInTheDocument()
    expect(screen.getByText(/verified source/i)).toBeInTheDocument()
    expect(screen.getByText(/informativa/i)).toBeInTheDocument()
    expect(screen.getByText(/claim one/i)).toBeInTheDocument()
    expect(screen.getByText(/first reason/i)).toBeInTheDocument()

    expect(fetchMock).toHaveBeenCalledWith('/analyze', expect.objectContaining({
      method: 'POST',
      body: expect.stringContaining('https://example.com/test-article'),
    }))
  })

  it('shows similar news section when available', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockApiResponse),
    } as Response)

    const user = userEvent.setup()
    render(<App />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://example.com/article')

    await user.click(screen.getByRole('button', { name: /analizar/i }))

    await waitFor(() => {
      expect(screen.getByText('REAL')).toBeInTheDocument()
    })

    await expect(screen.findByText(/related news/i)).resolves.toBeInTheDocument()
  })

  it('displays connection error when fetch fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Network failure'))

    const user = userEvent.setup()
    render(<App />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://example.com/bad')
    await user.click(screen.getByRole('button', { name: /analizar/i }))

    await waitFor(() => {
      expect(screen.getByText(/no se pudo conectar/i)).toBeInTheDocument()
    })
  })

  it('displays api error message', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ error: 'Invalid URL', analysis: null, similar_news: [], url_analyzed: '', article_text: '', domain: '', is_credible_source: false }),
    } as Response)

    const user = userEvent.setup()
    render(<App />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://invalid.com/url')
    await user.click(screen.getByRole('button', { name: /analizar/i }))

    await waitFor(() => {
      expect(screen.getByText(/invalid url/i)).toBeInTheDocument()
    })
  })

  it('clears results when clear button is clicked', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockApiResponse),
    } as Response)

    const user = userEvent.setup()
    render(<App />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://example.com/test')
    await user.click(screen.getByRole('button', { name: /analizar/i }))

    await waitFor(() => {
      expect(screen.getByText('REAL')).toBeInTheDocument()
    })

    const clearBtn = screen.getByTitle('Borrar')
    await user.click(clearBtn)

    await waitFor(() => {
      expect(screen.queryByText('REAL')).not.toBeInTheDocument()
    })
  })

  it('shows scam alert when analysis.is_scam is true', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        ...mockApiResponse,
        analysis: { ...mockApiResponse.analysis, is_scam: true, verdict: 'ESTAFA' },
      }),
    } as Response)

    const user = userEvent.setup()
    render(<App />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://example.com/scam')
    await user.click(screen.getByRole('button', { name: /analizar/i }))

    await waitFor(() => {
      expect(screen.getByText(/alerta de estafa/i)).toBeInTheDocument()
    })
  })
})
