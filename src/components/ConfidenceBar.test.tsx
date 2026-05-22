import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ConfidenceBar from './ConfidenceBar'

describe('ConfidenceBar', () => {
  it('renders score display', () => {
    render(<ConfidenceBar score={75} lang="es" />)
    expect(screen.getByText('75')).toBeInTheDocument()
  })

  it('shows Credibility Index in English', () => {
    render(<ConfidenceBar score={50} lang="en" />)
    expect(screen.getByText(/credibility index/i)).toBeInTheDocument()
  })

  it('shows Índice de Confiabilidad in Spanish', () => {
    render(<ConfidenceBar score={50} lang="es" />)
    expect(screen.getByText(/índice de confiabilidad/i)).toBeInTheDocument()
  })

  it('renders 20 segments', () => {
    const { container } = render(<ConfidenceBar score={50} lang="es" />)
    const segments = container.querySelectorAll('.conf-seg')
    expect(segments.length).toBe(20)
  })

  it('lights correct number of segments for score 50', () => {
    const { container } = render(<ConfidenceBar score={50} lang="es" />)
    const lit = container.querySelectorAll('.conf-seg.lit-orange')
    expect(lit.length).toBe(10)
  })

  it('lights correct number of segments for score 100', () => {
    const { container } = render(<ConfidenceBar score={100} lang="es" />)
    const lit = container.querySelectorAll('.conf-seg.lit-green')
    expect(lit.length).toBe(20)
  })

  it('uses red for score 0', () => {
    const { container } = render(<ConfidenceBar score={0} lang="es" />)
    const lit = container.querySelectorAll('.conf-seg.lit-red')
    expect(lit.length).toBe(0)
  })

  it('uses cyan for score 75', () => {
    const { container } = render(<ConfidenceBar score={75} lang="es" />)
    const lit = container.querySelectorAll('.conf-seg.lit-cyan')
    expect(lit.length).toBe(15)
  })
})
