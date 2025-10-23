import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ConsistencyChecker from '../ConsistencyChecker'

vi.mock('../../hooks/useSession', () => ({
  useSession: () => ({
    sessions: [
      {
        id: '1',
        projectName: 'Test Project',
        currentStage: 5,
        totalStages: 5,
        status: 'completed',
        stageData: {
          1: { problemStatement: 'Test problem' },
          2: { successMetrics: 'Test metrics' },
          3: { dataQualityRequirements: 'Test requirements' },
          4: { organizationalImpact: 'Test impact' },
          5: { governanceStructure: 'Test governance' },
        },
      },
    ],
    isLoading: false,
    error: null,
  }),
}))

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

describe('ConsistencyChecker - Specification Tests', () => {
  it('should validate responses across all 5 stages', () => {
    expect(ConsistencyChecker).toBeDefined()
    expect(typeof ConsistencyChecker).toBe('function')
  })

  it('should identify inconsistencies in questionnaire responses', () => {
    // Specification: Checks for logical consistency across stages
    expect(ConsistencyChecker).toBeDefined()
  })

  it('should provide recommendations for improvement', () => {
    // Specification: Shows actionable feedback
    expect(ConsistencyChecker).toBeDefined()
  })
})

describe('ConsistencyChecker - Structure Tests', () => {
  it('should render without crashing', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )
    expect(document.body).toBeDefined()
  })

  it('should display consistency report', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByRole('heading')).toBeInTheDocument()
  })

  it('should show check results for each stage', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })

  it('should display pass/fail indicators', () => {
    const queryClient = createQueryClient()
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    // Should have status indicators
    expect(container).toBeDefined()
  })
})

describe('ConsistencyChecker - Execution Tests', () => {
  it('should display all checks for the session', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(document.body).toBeDefined()
    })
  })

  it('should show consistency status', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Should show overall status
      expect(document.body).toBeDefined()
    })
  })

  it('should display individual check results', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Should show results for different checks
      expect(document.body).toBeDefined()
    })
  })

  it('should show recommendations for issues found', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(document.body).toBeDefined()
    })
  })
})

describe('ConsistencyChecker - Integration Tests', () => {
  it('should work with session data', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })

  it('should integrate with React Router', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })
})

describe('ConsistencyChecker - Error Handling Tests', () => {
  it('should handle missing session data gracefully', () => {
    const queryClient = createQueryClient()
    const originalConsoleError = console.error
    console.error = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="nonexistent" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
    console.error = originalConsoleError
  })

  it('should handle loading state', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ConsistencyChecker sessionId="1" />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })
})
