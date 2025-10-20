import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ErrorBoundary } from '../ErrorBoundary'

// Suppress console.error for error boundary tests
const originalError = console.error
beforeEach(() => {
  console.error = vi.fn()
})

afterEach(() => {
  console.error = originalError
})

const ThrowError = () => {
  throw new Error('Test error')
}

describe('ErrorBoundary Component', () => {
  it('should render children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    )
    
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('should render error message when child throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    
    expect(screen.getByText(/Something went wrong/)).toBeInTheDocument()
  })

  it('should display error details', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    
    expect(screen.getByText(/Test error/)).toBeInTheDocument()
  })

  it('should render retry button', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    
    expect(screen.getByRole('button', { name: /Try Again/ })).toBeInTheDocument()
  })

  it('should reset error state when retry is clicked', async () => {
    const user = userEvent.setup()
    let shouldThrow = true
    
    const ConditionalError = () => {
      if (shouldThrow) {
        throw new Error('Test error')
      }
      return <div>Success</div>
    }
    
    const { rerender } = render(
      <ErrorBoundary>
        <ConditionalError />
      </ErrorBoundary>
    )
    
    expect(screen.getByText(/Something went wrong/)).toBeInTheDocument()
    
    shouldThrow = false
    const retryButton = screen.getByRole('button', { name: /Try Again/ })
    await user.click(retryButton)
    
    rerender(
      <ErrorBoundary>
        <ConditionalError />
      </ErrorBoundary>
    )
    
    expect(screen.getByText('Success')).toBeInTheDocument()
  })

  it('should have error styling', () => {
    const { container } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    
    const errorDiv = container.querySelector('.bg-red-50')
    expect(errorDiv).toBeInTheDocument()
  })

  it('should display error icon', () => {
    const { container } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
  })

  it('should render with custom error message', () => {
    render(
      <ErrorBoundary errorMessage="Custom error occurred">
        <ThrowError />
      </ErrorBoundary>
    )
    
    expect(screen.getByText(/Custom error occurred/)).toBeInTheDocument()
  })

  it('should call onError callback when error occurs', () => {
    const onError = vi.fn()
    
    render(
      <ErrorBoundary onError={onError}>
        <ThrowError />
      </ErrorBoundary>
    )
    
    expect(onError).toHaveBeenCalled()
  })

  it('should render error boundary with proper structure', () => {
    const { container } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    
    const errorContainer = container.querySelector('.rounded-lg')
    expect(errorContainer).toHaveClass('shadow-lg')
  })
})

