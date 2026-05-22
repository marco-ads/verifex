import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LanguageToggle from './LanguageToggle'

describe('LanguageToggle', () => {
  it('shows EN when lang is es', () => {
    render(<LanguageToggle lang="es" onToggle={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'EN' })).toBeInTheDocument()
  })

  it('shows ES when lang is en', () => {
    render(<LanguageToggle lang="en" onToggle={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'ES' })).toBeInTheDocument()
  })

  it('calls onToggle on click', async () => {
    const onToggle = vi.fn()
    const user = userEvent.setup()
    render(<LanguageToggle lang="es" onToggle={onToggle} />)
    await user.click(screen.getByRole('button'))
    expect(onToggle).toHaveBeenCalledTimes(1)
  })
})
