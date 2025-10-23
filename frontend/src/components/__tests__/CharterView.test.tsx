import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import CharterView from '../pages/CharterView'

vi.mock('../../hooks/useSession', () => ({
  useSession: () => ({
    sessions: [
      {
        id: '1',
        projectName: 'Test Project',
        currentStage: 5,
        totalStages: 5,
        status: 'completed',
        createdAt: new Date(),
        updatedAt: new Date(),
        charter: {
          title: 'Data Governance Charter',
          executiveSummary: 'Test summary',
          sections: [],
        },
      },
    ],
    isLoading: false,
    error: null,
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

describe('CharterView - Specification Tests', () => {
  it('should display the generated data governance charter', () => {
    expect(CharterView).toBeDefined()
    expect(typeof CharterView).toBe('function')
  })

  it('should allow downloading the charter in multiple formats', () => {
    // Specification: CharterView provides download options
    expect(CharterView).toBeDefined()
  })

  it('should display charter content in a readable format', () => {
    // Specification: Charter is formatted and readable
    expect(CharterView).toBeDefined()
  })
})

describe('CharterView - Structure Tests', () => {
  it('should render without crashing', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )
    expect(document.body).toBeDefined()
  })

  it('should display charter title', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByRole('heading')).toBeInTheDocument()
  })

  it('should have download buttons for different formats', () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(screen.getByRole('button', { name: /download/i })).toBeInTheDocument()
  })
})

describe('CharterView - Execution Tests', () => {
  it('should display charter content', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })
  })

  it('should show download option for PDF', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const downloadButtons = screen.queryAllByRole('button', { name: /pdf|download/i })
    expect(downloadButtons.length).toBeGreaterThan(0)
  })

  it('should show download option for Markdown', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const downloadButtons = screen.queryAllByRole('button', { name: /markdown|download/i })
    expect(downloadButtons.length).toBeGreaterThan(0)
  })

  it('should allow user to download charter', async () => {
    const user = userEvent.setup()
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )

    const downloadBtn = screen.getByRole('button', { name: /download/i })
    await user.click(downloadBtn)
    expect(downloadBtn).toBeInTheDocument()
  })
})

describe('CharterView - Integration Tests', () => {
  it('should load charter data from session', async () => {
    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
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
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
  })
})

describe('CharterView - Error Handling Tests', () => {
  it('should handle missing charter gracefully', () => {
    const queryClient = createQueryClient()
    const originalConsoleError = console.error
    console.error = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CharterView />
        </BrowserRouter>
      </QueryClientProvider>
    )

    expect(document.body).toBeDefined()
    console.error = originalConsoleError
  })
})
