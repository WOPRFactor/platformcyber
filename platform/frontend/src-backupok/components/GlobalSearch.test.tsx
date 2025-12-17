import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import GlobalSearch from './GlobalSearch'

describe('GlobalSearch Component', () => {
  it('renders search input', () => {
    render(
      <BrowserRouter>
        <GlobalSearch />
      </BrowserRouter>
    )

    const input = screen.getByPlaceholderText(/Buscar módulos, páginas/i)
    expect(input).toBeInTheDocument()
  })

  it('allows typing in search input', () => {
    render(
      <BrowserRouter>
        <GlobalSearch />
      </BrowserRouter>
    )

    const input = screen.getByPlaceholderText(/Buscar módulos, páginas/i)

    // Escribir en el input
    fireEvent.change(input, { target: { value: 'test search' } })

    // Verificar que el valor cambió
    expect(input).toHaveValue('test search')
  })

  it('renders as a functional search component', () => {
    render(
      <BrowserRouter>
        <GlobalSearch />
      </BrowserRouter>
    )

    // Verificar que se renderiza correctamente
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })
})
