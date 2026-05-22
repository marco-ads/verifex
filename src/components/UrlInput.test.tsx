import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UrlInput from './UrlInput'

describe('UrlInput', () => {
  it('renders input and button in Spanish', () => {
    render(<UrlInput lang="es" loading={false} onAnalyze={vi.fn()} />)
    expect(screen.getByPlaceholderText(/ingresa una url/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analizar/i })).toBeInTheDocument()
  })

  it('renders input and button in English', () => {
    render(<UrlInput lang="en" loading={false} onAnalyze={vi.fn()} />)
    expect(screen.getByPlaceholderText(/enter a url/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze/i })).toBeInTheDocument()
  })

  it('shows analyzing state when loading', () => {
    render(<UrlInput lang="es" loading={true} onAnalyze={vi.fn()} />)
    expect(screen.getByRole('button', { name: /analizando/i })).toBeInTheDocument()
  })

  it('disables button when loading', () => {
    render(<UrlInput lang="es" loading={true} onAnalyze={vi.fn()} />)
    expect(screen.getByRole('button', { name: /analizando/i })).toBeDisabled()
  })

  it('disables button when url is empty', () => {
    render(<UrlInput lang="es" loading={false} onAnalyze={vi.fn()} />)
    expect(screen.getByRole('button', { name: /analizar/i })).toBeDisabled()
  })

  it('shows loading segments when loading', () => {
    render(<UrlInput lang="es" loading={true} onAnalyze={vi.fn()} />)
    expect(screen.getByText(/procesando señal/i)).toBeInTheDocument()
  })

  it('calls onAnalyze on form submit', async () => {
    const onAnalyze = vi.fn()
    const user = userEvent.setup()
    render(<UrlInput lang="es" loading={false} onAnalyze={onAnalyze} />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://example.com/news')
    await user.click(screen.getByRole('button', { name: /analizar/i }))

    expect(onAnalyze).toHaveBeenCalledWith('https://example.com/news')
  })

  it('calls onClear when clear button is clicked', async () => {
    const onClear = vi.fn()
    const user = userEvent.setup()
    render(<UrlInput lang="es" loading={false} onAnalyze={vi.fn()} onClear={onClear} />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://example.com')

    const clearBtn = screen.getByTitle('Borrar')
    await user.click(clearBtn)

    expect(onClear).toHaveBeenCalled()
  })

  it('does not call onAnalyze when loading', async () => {
    const onAnalyze = vi.fn()
    const user = userEvent.setup()
    render(<UrlInput lang="es" loading={true} onAnalyze={onAnalyze} />)

    const input = screen.getByPlaceholderText(/ingresa una url/i)
    await user.type(input, 'https://example.com/news')
    await user.click(screen.getByRole('button', { name: /analizando/i }))

    expect(onAnalyze).not.toHaveBeenCalled()
  })
})
