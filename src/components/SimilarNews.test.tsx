import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import SimilarNews from './SimilarNews'

const mockNews = [
  { title: 'Some news article', url: 'https://example.com/1', published: '2025-01-15', source: 'Source A' },
  { title: 'Another article', url: 'https://example.com/2', published: '2025-02-20', source: 'Source B' },
]

describe('SimilarNews', () => {
  it('returns null when news is empty', () => {
    const { container } = render(<SimilarNews news={[]} lang="es" />)
    expect(container.innerHTML).toBe('')
  })

  it('returns null when news is undefined', () => {
    const { container } = render(<SimilarNews news={[]} lang="es" />)
    expect(container.innerHTML).toBe('')
  })

  it('renders Noticias Similares in Spanish', () => {
    render(<SimilarNews news={mockNews} lang="es" />)
    expect(screen.getByText(/noticias similares/i)).toBeInTheDocument()
  })

  it('renders Similar News in English', () => {
    render(<SimilarNews news={mockNews} lang="en" />)
    expect(screen.getByText(/similar news/i)).toBeInTheDocument()
  })

  it('renders news titles', () => {
    render(<SimilarNews news={mockNews} lang="es" />)
    expect(screen.getByText('Some news article')).toBeInTheDocument()
    expect(screen.getByText('Another article')).toBeInTheDocument()
  })

  it('renders news sources', () => {
    render(<SimilarNews news={mockNews} lang="es" />)
    expect(screen.getByText('Source A')).toBeInTheDocument()
    expect(screen.getByText('Source B')).toBeInTheDocument()
  })

  it('renders news items as links with correct href', () => {
    render(<SimilarNews news={mockNews} lang="es" />)
    const links = screen.getAllByRole('link')
    expect(links[0]).toHaveAttribute('href', 'https://example.com/1')
    expect(links[1]).toHaveAttribute('href', 'https://example.com/2')
  })

  it('opens links in new tab', () => {
    render(<SimilarNews news={mockNews} lang="es" />)
    const links = screen.getAllByRole('link')
    links.forEach(link => {
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })
})
