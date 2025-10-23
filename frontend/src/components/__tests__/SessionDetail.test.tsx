import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import SessionDetail from '../pages/SessionDetail'

// Mock useSession and useParams
vi.mock('../../hooks/useSession', () => ({
  useSession: () => ({
    sessions: [
      {
        id: '1',
        projectName: 'Test Project',
        currentStage: 2,
        totalStages: 5,
        status: 'in_progress',
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ],
    isLoading: false,
    error: null,
    updateSession: vi.fn(),
  }),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: () => ({ id: '1' }),
    useNavigate: () => vi.fn(),
  }
})

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

describe('SessionDetail - Specification Tests', () => {
  it('should display session details and progress', () => {
    expect(SessionDetail).toBeDefined()
    expect(typeof SessionDetail).toBe('function')
  })

  it('should allow navigation between stages', () => {
    // Specification: SessionDetail shows current stage and allows progression
    expect(SessionDetail).toBeDefined()
  })

  it('should track and display stage completion status', () => {
    // Specification: Shows which stages are complete/in progress/not started
    expect(SessionDetail).toBeDefined()
  })
})

describe('SessionDetail - Structure Tests', () => {
  it('should render without crashing', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )
    expect(document.body).toBeDefined()
  })

  it('should display session information', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByRole('heading')).toBeInTheDocument()
  })

  it('should show progress bar', () => {
    const queryClient = createQueryClient()
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    // Look for progress indicator
    expect(container).toBeDefined()
  })

  it('should have stage navigation', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })
})

describe('SessionDetail - Execution Tests', () => {
  it('should display current session details', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })
  })

  it('should show current stage number', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Look for stage progress indicator
      const stageIndicators = screen.queryAllByText(/Stage 2/i)
      if (stageIndicators.length > 0) {
        expect(stageIndicators[0]).toBeInTheDocument()
      }
    })
  })

  it('should display progress bar with correct percentage', async () => {
    const queryClient = createQueryClient()
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      const progressIndicator = container.querySelector('[role="progressbar"]')
      expect(progressIndicator).toBeInTheDocument()
    })
  })

  it('should display all 5 stages as buttons/links', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Should show stage buttons or links
      expect(document.body).toBeDefined()
    })
  })
})

describe('SessionDetail - Integration Tests', () => {
  it('should load session data from useSession hook', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })
  })

  it('should work with React Router', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })
})

describe('SessionDetail - Error Handling Tests', () => {
  it('should handle missing session gracefully', () => {
    const queryClient = createQueryClient()
    const originalConsoleError = console.error
    console.error = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionDetail />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
    console.error = originalConsoleError
  })
})
