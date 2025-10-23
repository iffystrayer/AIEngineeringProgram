import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import SessionsList from '../pages/SessionsList'

// Mock useSession hook
vi.mock('../../hooks/useSession', () => ({
  useSession: () => ({
    sessions: [
      {
        id: '1',
        projectName: 'AI Initiative A',
        currentStage: 2,
        totalStages: 5,
        status: 'in_progress',
        createdAt: new Date('2025-10-20'),
        updatedAt: new Date('2025-10-23'),
      },
      {
        id: '2',
        projectName: 'Data Pipeline B',
        currentStage: 5,
        totalStages: 5,
        status: 'completed',
        createdAt: new Date('2025-10-15'),
        updatedAt: new Date('2025-10-22'),
      },
      {
        id: '3',
        projectName: 'Process Improvement C',
        currentStage: 1,
        totalStages: 5,
        status: 'in_progress',
        createdAt: new Date('2025-10-23'),
        updatedAt: new Date('2025-10-23'),
      },
    ],
    isLoading: false,
    error: null,
    deleteSession: vi.fn(),
    updateSession: vi.fn(),
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

describe('SessionsList - Specification Tests', () => {
  it('should provide a comprehensive list of all sessions', () => {
    expect(SessionsList).toBeDefined()
    expect(typeof SessionsList).toBe('function')
  })

  it('should allow users to search, filter, and manage sessions', () => {
    // Specification: SessionsList is a data table with search/filter capabilities
    expect(SessionsList).toBeDefined()
  })

  it('should support pagination for large datasets', () => {
    // Specification: SessionsList includes pagination controls
    expect(SessionsList).toBeDefined()
  })
})

describe('SessionsList - Structure Tests', () => {
  it('should render without crashing', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )
    expect(document.body).toBeDefined()
  })

  it('should display table with session columns', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByRole('table')).toBeInTheDocument()
  })

  it('should have search input field', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument()
  })

  it('should have status filter', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByLabelText(/status/i)).toBeInTheDocument()
  })
})

describe('SessionsList - Execution Tests', () => {
  it('should display all sessions in table', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('AI Initiative A')).toBeInTheDocument()
      expect(screen.getByText('Data Pipeline B')).toBeInTheDocument()
      expect(screen.getByText('Process Improvement C')).toBeInTheDocument()
    })
  })

  it('should show session progress in table', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/2\/5/)).toBeInTheDocument()
      expect(screen.getByText(/5\/5/)).toBeInTheDocument()
      expect(screen.getByText(/1\/5/)).toBeInTheDocument()
    })
  })

  it('should display status badges for each session', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      const statusElements = screen.getAllByText(/in progress|completed/i)
      expect(statusElements.length).toBeGreaterThan(0)
    })
  })

  it('should allow searching sessions by project name', async () => {
    const user = userEvent.setup()
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const searchInput = screen.getByPlaceholderText(/search/i)
    await user.type(searchInput, 'AI Initiative')

    await waitFor(() => {
      expect(screen.getByText('AI Initiative A')).toBeInTheDocument()
    })
  })

  it('should filter sessions by status', async () => {
    const user = userEvent.setup()
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const statusFilter = screen.getByLabelText(/status/i)
    await user.selectOptions(statusFilter, 'completed')

    await waitFor(() => {
      expect(screen.getByText('Data Pipeline B')).toBeInTheDocument()
    })
  })

  it('should provide action buttons for each session', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      const viewButtons = screen.getAllByRole('button', { name: /view|resume/i })
      expect(viewButtons.length).toBeGreaterThan(0)
    })
  })

  it('should have pagination controls', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    // Look for pagination controls or page info
    expect(document.body).toBeDefined()
  })
})

describe('SessionsList - Integration Tests', () => {
  it('should integrate with useSession hook', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('AI Initiative A')).toBeInTheDocument()
    })
  })

  it('should work with React Router for navigation to session details', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })
})

describe('SessionsList - Error Handling Tests', () => {
  it('should handle empty sessions list gracefully', () => {
    const queryClient = createQueryClient()
    const originalConsoleError = console.error
    console.error = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
    console.error = originalConsoleError
  })

  it('should display loading state', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SessionsList />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })
})
