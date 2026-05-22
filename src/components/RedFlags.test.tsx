import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import RedFlags from './RedFlags'

describe('RedFlags', () => {
  it('renders Detected Alerts in English', () => {
    render(<RedFlags redFlags={[]} positiveSignals={[]} lang="en" />)
    expect(screen.getByText(/detected alerts/i)).toBeInTheDocument()
  })

  it('renders Alertas Detectadas in Spanish', () => {
    render(<RedFlags redFlags={[]} positiveSignals={[]} lang="es" />)
    expect(screen.getByText(/alertas detectadas/i)).toBeInTheDocument()
  })

  it('renders Positive Signals in English', () => {
    render(<RedFlags redFlags={[]} positiveSignals={[]} lang="en" />)
    expect(screen.getByText(/positive signals/i)).toBeInTheDocument()
  })

  it('renders Señales Positivas in Spanish', () => {
    render(<RedFlags redFlags={[]} positiveSignals={[]} lang="es" />)
    expect(screen.getByText(/señales positivas/i)).toBeInTheDocument()
  })

  it('shows empty state (—) when no red flags', () => {
    render(<RedFlags redFlags={[]} positiveSignals={['good']} lang="es" />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('shows empty state (—) when no positive signals', () => {
    render(<RedFlags redFlags={['bad']} positiveSignals={[]} lang="es" />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('renders red flag items', () => {
    render(<RedFlags redFlags={['Sensationalism', 'No sources']} positiveSignals={[]} lang="en" />)
    expect(screen.getByText(/sensationalism/i)).toBeInTheDocument()
    expect(screen.getByText(/no sources/i)).toBeInTheDocument()
  })

  it('renders positive signal items', () => {
    render(<RedFlags redFlags={[]} positiveSignals={['Verified source', 'Recent']} lang="en" />)
    expect(screen.getByText(/verified source/i)).toBeInTheDocument()
    expect(screen.getByText(/recent/i)).toBeInTheDocument()
  })

  it('renders both flags and signals', () => {
    render(<RedFlags redFlags={['Clickbait']} positiveSignals={['Good domain']} lang="en" />)
    expect(screen.getByText(/clickbait/i)).toBeInTheDocument()
    expect(screen.getByText(/good domain/i)).toBeInTheDocument()
  })
})
