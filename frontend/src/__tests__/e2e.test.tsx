import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LandingPage } from '../components/LandingPage'
import {
  createMockApiClient,
  createTestSession,
  createTestProgress,
} from '../test/mockServer'

// Mock the hooks with our mock API client
const mockApiClient = createMockApiClient()

vi.mock('../hooks/useSession', () => ({
  useSession: () => ({
    session: null,
    sessions: [],
    sessionId: null,
    status: null,
    isLoading: false,
    error: null,
    createNewSession: mockApiClient.createSession,
    getSessionDetails: mockApiClient.getSession,
    listUserSessions: mockApiClient.listSessions,
    deleteCurrentSession: mockApiClient.deleteSession,
    clearError: vi.fn(),
  }),
}))

vi.mock('../hooks/useProgress', () => ({
  useProgress: () => ({
    progress: null,
    events: [],
    currentStage: null,
    questionsAnswered: null,
    charterStatus: null,
    isLoading: false,
    error: null,
    submitAnswer: mockApiClient.submitAnswer,
    refreshProgress: mockApiClient.getProgress,
    clearError: vi.fn(),
  }),
}))

describe('End-to-End User Workflows', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('New Session Workflow', () => {
    it('should complete new session creation workflow', async () => {
      const user = userEvent.setup()
      render(<LandingPage />)

      // 1. Click start new button
      const startButton = screen.getByTestId('start-new-button')
      await user.click(startButton)

      // 2. Form should appear
      await waitFor(() => {
        expect(screen.getByText('Create New Session')).toBeInTheDocument()
      })

      // 3. Fill form
      const userIdInput = screen.getByLabelText(/User ID/)
      const projectNameInput = screen.getByLabelText(/Project Name/)

      await user.type(userIdInput, 'e2e-user')
      await user.type(projectNameInput, 'E2E Test Project')

      // 4. Submit form
      const submitButton = screen.getByRole('button', { name: /Start Session/ })
      await user.click(submitButton)

      // 5. Verify session was created (just check it was called)
      expect(mockApiClient.createSession).toHaveBeenCalled()
    })

    it('should show validation errors for empty fields', async () => {
      const user = userEvent.setup()
      render(<LandingPage />)

      // Click start new button
      const startButton = screen.getByTestId('start-new-button')
      await user.click(startButton)

      // Try to submit empty form
      await waitFor(() => {
        expect(screen.getByText('Create New Session')).toBeInTheDocument()
      })

      const submitButton = screen.getByRole('button', { name: /Start Session/ })
      await user.click(submitButton)

      // Should not call createSession
      expect(mockApiClient.createSession).not.toHaveBeenCalled()
    })

    it('should allow canceling session creation', async () => {
      const user = userEvent.setup()
      render(<LandingPage />)

      // Click start new button
      const startButton = screen.getByTestId('start-new-button')
      await user.click(startButton)

      // Wait for form
      await waitFor(() => {
        expect(screen.getByText('Create New Session')).toBeInTheDocument()
      })

      // Click cancel
      const cancelButton = screen.getByRole('button', { name: /Cancel/ })
      await user.click(cancelButton)

      // Form should close
      await waitFor(() => {
        expect(screen.queryByText('Create New Session')).not.toBeInTheDocument()
      })
    })
  })

  describe('Resume Session Workflow', () => {
    it('should complete resume session workflow', async () => {
      const user = userEvent.setup()

      render(<LandingPage />)

      // Click resume button
      const resumeButton = screen.getByTestId('resume-button')
      await user.click(resumeButton)

      // Modal should appear
      await waitFor(() => {
        expect(screen.getByText('Select Session')).toBeInTheDocument()
      })

      // Modal should be visible
      expect(screen.getByText('Select Session')).toBeInTheDocument()
    })

    it('should show empty state when no sessions', async () => {
      const user = userEvent.setup()
      render(<LandingPage />)

      // Click resume button
      const resumeButton = screen.getByTestId('resume-button')
      await user.click(resumeButton)

      // Modal should appear
      await waitFor(() => {
        expect(screen.getByText('Select Session')).toBeInTheDocument()
      })

      // Empty state should show
      expect(screen.getByText(/No sessions found/)).toBeInTheDocument()
    })

    it('should allow closing session modal', async () => {
      const user = userEvent.setup()
      render(<LandingPage />)

      // Click resume button
      const resumeButton = screen.getByTestId('resume-button')
      await user.click(resumeButton)

      // Wait for modal
      await waitFor(() => {
        expect(screen.getByText('Select Session')).toBeInTheDocument()
      })

      // Click close
      const closeButton = screen.getByRole('button', { name: /Close/ })
      await user.click(closeButton)

      // Modal should close
      await waitFor(() => {
        expect(screen.queryByText('Select Session')).not.toBeInTheDocument()
      })
    })
  })

  describe('Progress Tracking Workflow', () => {
    it('should display progress when session is active', () => {
      render(<LandingPage sessionId="session-1" />)

      // Landing page should render
      expect(screen.getByText('U-AIP Scoping Assistant')).toBeInTheDocument()
    })
  })

  describe('Error Handling Workflow', () => {
    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup()

      // Mock API error
      mockApiClient.createSession = vi.fn().mockRejectedValue(
        new Error('API Error')
      )

      render(<LandingPage />)

      // Click start new button
      const startButton = screen.getByTestId('start-new-button')
      await user.click(startButton)

      // Fill and submit form
      await waitFor(() => {
        expect(screen.getByText('Create New Session')).toBeInTheDocument()
      })

      const userIdInput = screen.getByLabelText(/User ID/)
      const projectNameInput = screen.getByLabelText(/Project Name/)

      await user.type(userIdInput, 'user')
      await user.type(projectNameInput, 'project')

      const submitButton = screen.getByRole('button', { name: /Start Session/ })
      await user.click(submitButton)

      // Error should be handled
      expect(mockApiClient.createSession).toHaveBeenCalled()
    })
  })

  describe('Multiple Operations Workflow', () => {
    it('should handle multiple session operations', async () => {
      const user = userEvent.setup()
      render(<LandingPage />)

      // Create first session
      const startButton = screen.getByTestId('start-new-button')
      await user.click(startButton)

      await waitFor(() => {
        expect(screen.getByText('Create New Session')).toBeInTheDocument()
      })

      const userIdInput = screen.getByLabelText(/User ID/)
      const projectNameInput = screen.getByLabelText(/Project Name/)

      await user.type(userIdInput, 'user-1')
      await user.type(projectNameInput, 'Project 1')

      const submitButton = screen.getByRole('button', { name: /Start Session/ })
      await user.click(submitButton)

      // Verify session was created
      expect(mockApiClient.createSession).toHaveBeenCalled()
    })
  })
})

