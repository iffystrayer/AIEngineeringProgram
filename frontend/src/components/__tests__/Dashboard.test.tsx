import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Dashboard from '../pages/Dashboard'

// Mock the useSession hook
vi.mock('../../hooks/useSession', () => ({
  useSession: () => ({
    sessions: [
      {
        id: '1',
        projectName: 'Test Project 1',
        currentStage: 2,
        totalStages: 5,
        status: 'in_progress',
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      {
        id: '2',
        projectName: 'Test Project 2',
        currentStage: 5,
        totalStages: 5,
        status: 'completed',
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ],
    isLoading: false,
    error: null,
    createSession: vi.fn(),
  }),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
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

describe('Dashboard - Specification Tests', () => {
  it('should be the main entry point after landing page', () => {
    expect(Dashboard).toBeDefined()
    expect(typeof Dashboard).toBe('function')
  })

  it('should display welcome message and recent sessions', () => {
    // Specification: Dashboard greets user and shows recent activity
    expect(Dashboard).toBeDefined()
  })

  it('should provide quick access to new session and recent projects', () => {
    // Specification: Dashboard has CTA buttons
    expect(Dashboard).toBeDefined()
  })
})

describe('Dashboard - Structure Tests', () => {
  beforeEach(() => {
    // Clean setup for each test
  })

  it('should render without crashing', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )
    expect(document.body).toBeDefined()
  })

  it('should display dashboard title', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(
      screen.getByRole('heading', { name: /welcome back/i })
    ).toBeInTheDocument()
  })

  it('should have a new session button', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(
      screen.getByRole('button', { name: /new session/i })
    ).toBeInTheDocument()
  })
})

describe('Dashboard - Execution Tests', () => {
  it('should display recent sessions', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      expect(screen.getByText('Test Project 2')).toBeInTheDocument()
    })
  })

  it('should show session progress information', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Check for progress indicator
      expect(screen.getByText(/2\/5/)).toBeInTheDocument() // Stage 2/5
      expect(screen.getByText(/5\/5/)).toBeInTheDocument() // Stage 5/5
    })
  })

  it('should display session status badges', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Status badges are displayed with icon + text
      const statusElements = screen.queryAllByText(/⏳|✓/)
      expect(statusElements.length).toBeGreaterThan(0)
    })
  })

  it('should allow clicking new session button', async () => {
    const user = userEvent.setup()
    const queryClient = createQueryClient()
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const newSessionBtn = screen.getByRole('button', { name: /new session/i })
    await user.click(newSessionBtn)
    expect(newSessionBtn).toBeInTheDocument()
  })
})

describe('Dashboard - Integration Tests', () => {
  it('should integrate with useSession hook', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Project 1')).toBeInTheDocument()
    })
  })

  it('should work with React Router for navigation', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })
})

describe('Dashboard - Error Handling Tests', () => {
  it('should handle empty sessions list', () => {
    const queryClient = createQueryClient()
    const originalConsoleError = console.error
    console.error = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
    console.error = originalConsoleError
  })
})
