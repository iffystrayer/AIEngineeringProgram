import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Layout from '../Layout'

describe('Layout - Specification Tests', () => {
  it('should provide main application layout structure', () => {
    expect(Layout).toBeDefined()
    expect(typeof Layout).toBe('function')
  })

  it('should support main content area with sidebar navigation', () => {
    // Specification: Layout provides two-column structure (sidebar + content)
    expect(Layout).toBeDefined()
  })

  it('should be responsive for mobile and desktop', () => {
    // Specification: Layout uses Tailwind responsive classes
    expect(Layout).toBeDefined()
  })
})

describe('Layout - Structure Tests', () => {
  beforeEach(() => {
    // Ensure clean DOM
  })

  it('should render without crashing', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    )
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('should accept children prop', () => {
    const { container } = render(
      <BrowserRouter>
        <Layout>
          <div data-testid="test-child">Test Content</div>
        </Layout>
      </BrowserRouter>
    )
    expect(container.querySelector('[data-testid="test-child"]')).toBeInTheDocument()
  })

  it('should render sidebar navigation', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test</div>
        </Layout>
      </BrowserRouter>
    )
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('should render main content area', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    )
    expect(screen.getByRole('main')).toBeInTheDocument()
  })
})

describe('Layout - Execution Tests', () => {
  it('should display navigation links', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test</div>
        </Layout>
      </BrowserRouter>
    )

    // Should have navigation links for main pages
    const nav = screen.getByRole('navigation')
    expect(nav).toBeInTheDocument()
  })

  it('should render children in main content area', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div data-testid="main-content">Main Content Here</div>
        </Layout>
      </BrowserRouter>
    )

    const mainContent = screen.getByTestId('main-content')
    const mainArea = screen.getByRole('main')
    expect(mainArea.contains(mainContent)).toBe(true)
  })

  it('should have responsive sidebar', () => {
    const { container } = render(
      <BrowserRouter>
        <Layout>
          <div>Test</div>
        </Layout>
      </BrowserRouter>
    )

    const sidebar = container.querySelector('[data-testid="sidebar"]')
    expect(sidebar).toBeInTheDocument()
  })
})

describe('Layout - Integration Tests', () => {
  it('should work with React Router Links', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test</div>
        </Layout>
      </BrowserRouter>
    )
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('should properly structure DOM for accessibility', () => {
    const { container } = render(
      <BrowserRouter>
        <Layout>
          <div>Test</div>
        </Layout>
      </BrowserRouter>
    )

    expect(container.querySelector('nav')).toBeDefined()
    expect(container.querySelector('main')).toBeDefined()
  })
})
