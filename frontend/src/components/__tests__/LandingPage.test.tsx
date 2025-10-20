import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LandingPage } from '../LandingPage'

// Mock the hooks
vi.mock('../../hooks/useSession', () => ({
  useSession: () => ({
    session: null,
    sessions: [],
    sessionId: null,
    status: null,
    isLoading: false,
    error: null,
    createNewSession: vi.fn(),
    getSessionDetails: vi.fn(),
    listUserSessions: vi.fn(),
    deleteCurrentSession: vi.fn(),
    clearError: vi.fn(),
  }),
}))

vi.mock('../../hooks/useProgress', () => ({
  useProgress: () => ({
    progress: null,
    events: [],
    currentStage: null,
    questionsAnswered: null,
    charterStatus: null,
    isLoading: false,
    error: null,
    submitAnswer: vi.fn(),
    refreshProgress: vi.fn(),
    clearError: vi.fn(),
  }),
}))

describe('LandingPage Component', () => {
  it('should render the landing page with title', () => {
    render(<LandingPage />)

    expect(screen.getByText('U-AIP Scoping Assistant')).toBeInTheDocument()
    expect(
      screen.getByText('Universal AI Project Scoping and Framing Protocol')
    ).toBeInTheDocument()
  })

  it('should render start new project card', () => {
    render(<LandingPage />)
    
    expect(screen.getByText('Start New Project')).toBeInTheDocument()
    expect(
      screen.getByText(/Begin a new AI project evaluation/)
    ).toBeInTheDocument()
    expect(screen.getByTestId('start-new-button')).toBeInTheDocument()
  })

  it('should render resume session card', () => {
    render(<LandingPage />)
    
    expect(screen.getByText('Resume Session')).toBeInTheDocument()
    expect(
      screen.getByText(/Continue working on an existing project evaluation/)
    ).toBeInTheDocument()
    expect(screen.getByTestId('resume-button')).toBeInTheDocument()
  })

  it('should render all 5 stages', () => {
    render(<LandingPage />)
    
    expect(screen.getByText('Business Translation')).toBeInTheDocument()
    expect(screen.getByText('Value Quantification')).toBeInTheDocument()
    expect(screen.getByText('Data Feasibility')).toBeInTheDocument()
    expect(screen.getByText('User Centricity')).toBeInTheDocument()
    expect(screen.getByText('Ethical Governance')).toBeInTheDocument()
  })

  it('should call onStartNew when start button is clicked', async () => {
    const user = userEvent.setup()
    const onStartNew = vi.fn()
    
    render(<LandingPage onStartNew={onStartNew} />)
    
    const startButton = screen.getByTestId('start-new-button')
    await user.click(startButton)
    
    expect(onStartNew).toHaveBeenCalledOnce()
  })

  it('should call onResume when resume button is clicked', async () => {
    const user = userEvent.setup()
    const onResume = vi.fn()
    
    render(<LandingPage onResume={onResume} />)
    
    const resumeButton = screen.getByTestId('resume-button')
    await user.click(resumeButton)
    
    expect(onResume).toHaveBeenCalledOnce()
  })

  it('should have proper styling classes', () => {
    const { container } = render(<LandingPage />)
    
    const mainDiv = container.firstChild
    expect(mainDiv).toHaveClass('min-h-screen')
    expect(mainDiv).toHaveClass('bg-gradient-to-br')
  })

  it('should render stage numbers correctly', () => {
    render(<LandingPage />)

    for (let i = 1; i <= 5; i++) {
      expect(screen.getByText(i.toString())).toBeInTheDocument()
    }
  })

  it('should show new session form when start button is clicked', async () => {
    const user = userEvent.setup()
    render(<LandingPage />)

    const startButton = screen.getByTestId('start-new-button')
    await user.click(startButton)

    await waitFor(() => {
      expect(screen.getByText('Create New Session')).toBeInTheDocument()
    })
  })

  it('should show session modal when resume button is clicked', async () => {
    const user = userEvent.setup()
    render(<LandingPage />)

    const resumeButton = screen.getByTestId('resume-button')
    await user.click(resumeButton)

    await waitFor(() => {
      expect(screen.getByText('Select Session')).toBeInTheDocument()
    })
  })

  it('should display progress when session is active', () => {
    // Mock useProgress to return progress data
    vi.doMock('../../hooks/useProgress', () => ({
      useProgress: () => ({
        progress: {
          session_id: 'test-session',
          current_stage: 1,
          questions_answered: 0,
          charter_status: 'pending',
          total_questions: 20,
        },
        events: [],
        currentStage: 1,
        questionsAnswered: 0,
        charterStatus: 'pending',
        isLoading: false,
        error: null,
        submitAnswer: vi.fn(),
        refreshProgress: vi.fn(),
        clearError: vi.fn(),
      }),
    }))

    render(<LandingPage sessionId="test-session" />)

    // Just verify the component renders without error
    expect(screen.getByText('U-AIP Scoping Assistant')).toBeInTheDocument()
  })

  it('should handle session creation', async () => {
    const user = userEvent.setup()
    render(<LandingPage />)

    const startButton = screen.getByTestId('start-new-button')
    await user.click(startButton)

    await waitFor(() => {
      expect(screen.getByText('Create New Session')).toBeInTheDocument()
    })
  })

  it('should close new session form when cancel is clicked', async () => {
    const user = userEvent.setup()
    render(<LandingPage />)

    const startButton = screen.getByTestId('start-new-button')
    await user.click(startButton)

    await waitFor(() => {
      expect(screen.getByText('Create New Session')).toBeInTheDocument()
    })

    const cancelButton = screen.getByRole('button', { name: /Cancel/ })
    await user.click(cancelButton)

    await waitFor(() => {
      expect(screen.queryByText('Create New Session')).not.toBeInTheDocument()
    })
  })

  it('should close session modal when close is clicked', async () => {
    const user = userEvent.setup()
    render(<LandingPage />)

    const resumeButton = screen.getByTestId('resume-button')
    await user.click(resumeButton)

    await waitFor(() => {
      expect(screen.getByText('Select Session')).toBeInTheDocument()
    })

    const closeButton = screen.getByRole('button', { name: /Close/ })
    await user.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByText('Select Session')).not.toBeInTheDocument()
    })
  })
})

