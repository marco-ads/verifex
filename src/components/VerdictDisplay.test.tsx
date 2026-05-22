import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import VerdictDisplay from './VerdictDisplay'

describe('VerdictDisplay', () => {
  it('renders REAL verdict in Spanish', () => {
    render(<VerdictDisplay verdict="REAL" lang="es" />)
    expect(screen.getByText('REAL')).toBeInTheDocument()
    expect(screen.getByText(/información verificada y legítima/i)).toBeInTheDocument()
  })

  it('renders REAL verdict in English', () => {
    render(<VerdictDisplay verdict="REAL" lang="en" />)
    expect(screen.getByText('REAL')).toBeInTheDocument()
    expect(screen.getByText(/verified and legitimate/i)).toBeInTheDocument()
  })

  it('renders FALSO verdict', () => {
    render(<VerdictDisplay verdict="FALSO" lang="es" />)
    expect(screen.getByText('FALSO')).toBeInTheDocument()
  })

  it('renders SÁTIRA verdict', () => {
    render(<VerdictDisplay verdict="SÁTIRA" lang="es" />)
    expect(screen.getByText('SÁTIRA')).toBeInTheDocument()
  })

  it('renders ESTAFA verdict', () => {
    render(<VerdictDisplay verdict="ESTAFA" lang="es" />)
    expect(screen.getByText('ESTAFA')).toBeInTheDocument()
  })

  it('renders NO VERIFICABLE verdict', () => {
    render(<VerdictDisplay verdict="NO VERIFICABLE" lang="es" />)
    expect(screen.getByText('NO VERIFICABLE')).toBeInTheDocument()
  })

  it('falls back to NO VERIFICABLE for unknown verdict', () => {
    render(<VerdictDisplay verdict="INVALID" lang="es" />)
    expect(screen.getByText('INVALID')).toBeInTheDocument()
  })
})
