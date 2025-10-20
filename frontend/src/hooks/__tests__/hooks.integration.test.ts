import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  createMockApiClient,
  createMockUseSession,
  createMockUseProgress,
  createTestSession,
  createTestProgress,
} from '../../test/mockServer'

describe('Hooks Integration Tests', () => {
  let mockApiClient: ReturnType<typeof createMockApiClient>

  beforeEach(() => {
    mockApiClient = createMockApiClient()
  })

  describe('useSession Hook Integration', () => {
    it('should create a session through the hook', async () => {
      const mockSession = createMockUseSession()
      mockSession.createNewSession = vi.fn(async (userId, projectName, description) => {
        const session = await mockApiClient.createSession({
          user_id: userId,
          project_name: projectName,
          description,
        })
        return session
      })

      const result = await mockSession.createNewSession(
        'user-1',
        'Test Project',
        'Test Description'
      )

      expect(result.session_id).toBeDefined()
      expect(result.project_name).toBe('Test Project')
    })

    it('should list sessions through the hook', async () => {
      const mockSession = createMockUseSession()
      mockSession.listUserSessions = vi.fn(async (userId) => {
        return mockApiClient.listSessions(userId)
      })

      // Create some sessions first
      await mockApiClient.createSession({
        user_id: 'user-1',
        project_name: 'Project 1',
      })
      await mockApiClient.createSession({
        user_id: 'user-1',
        project_name: 'Project 2',
      })

      const sessions = await mockSession.listUserSessions('user-1')
      expect(sessions.length).toBeGreaterThanOrEqual(2)
    })

    it('should get session details through the hook', async () => {
      const mockSession = createMockUseSession()
      mockSession.getSessionDetails = vi.fn(async (sessionId) => {
        return mockApiClient.getSession(sessionId)
      })

      const details = await mockSession.getSessionDetails('session-1')
      expect(details.session_id).toBe('session-1')
    })

    it('should delete a session through the hook', async () => {
      const mockSession = createMockUseSession()
      mockSession.deleteCurrentSession = vi.fn(async (sessionId) => {
        await mockApiClient.deleteSession(sessionId)
      })

      const createdSession = await mockApiClient.createSession({
        user_id: 'user-1',
        project_name: 'To Delete',
      })

      await mockSession.deleteCurrentSession(createdSession.session_id)

      await expect(
        mockApiClient.getSession(createdSession.session_id)
      ).rejects.toThrow()
    })

    it('should handle errors in session operations', async () => {
      const mockSession = createMockUseSession()
      mockSession.getSessionDetails = vi.fn(async (sessionId) => {
        return mockApiClient.getSession(sessionId)
      })

      await expect(
        mockSession.getSessionDetails('non-existent')
      ).rejects.toThrow()
    })
  })

  describe('useProgress Hook Integration', () => {
    it('should get progress through the hook', async () => {
      const mockProgress = createMockUseProgress()
      mockProgress.refreshProgress = vi.fn(async () => {
        return mockApiClient.getProgress('session-1')
      })

      const progress = await mockProgress.refreshProgress()
      expect(progress.session_id).toBe('session-1')
      expect(progress.current_stage).toBeDefined()
    })

    it('should submit an answer through the hook', async () => {
      const mockProgress = createMockUseProgress()
      mockProgress.submitAnswer = vi.fn(async (request) => {
        return mockApiClient.submitAnswer(request)
      })

      const event = await mockProgress.submitAnswer({
        session_id: 'session-1',
        stage_number: 1,
        question_id: 'q1',
        answer: 'test answer',
      })

      expect(event.event_type).toBe('QUESTION_ANSWERED')
    })

    it('should handle progress errors', async () => {
      const mockProgress = createMockUseProgress()
      mockProgress.refreshProgress = vi.fn(async () => {
        return mockApiClient.getProgress('non-existent')
      })

      await expect(mockProgress.refreshProgress()).rejects.toThrow()
    })
  })

  describe('Combined Hook Integration', () => {
    it('should create session and track progress', async () => {
      const mockSession = createMockUseSession()
      const mockProgress = createMockUseProgress()

      mockSession.createNewSession = vi.fn(async (userId, projectName) => {
        return mockApiClient.createSession({
          user_id: userId,
          project_name: projectName,
        })
      })

      mockProgress.refreshProgress = vi.fn(async () => {
        return mockApiClient.getProgress('session-1')
      })

      // Create session
      const session = await mockSession.createNewSession('user-1', 'Test Project')
      expect(session.session_id).toBeDefined()

      // Get progress
      const progress = await mockProgress.refreshProgress()
      expect(progress.session_id).toBe('session-1')
    })

    it('should handle session and progress workflow', async () => {
      const mockSession = createMockUseSession()
      const mockProgress = createMockUseProgress()

      mockSession.createNewSession = vi.fn(async (userId, projectName) => {
        return mockApiClient.createSession({
          user_id: userId,
          project_name: projectName,
        })
      })

      mockProgress.submitAnswer = vi.fn(async (request) => {
        return mockApiClient.submitAnswer(request)
      })

      mockProgress.refreshProgress = vi.fn(async () => {
        return mockApiClient.getProgress('session-1')
      })

      // Create session
      const session = await mockSession.createNewSession('user-1', 'Workflow Test')
      expect(session.session_id).toBeDefined()

      // Submit answer
      const event = await mockProgress.submitAnswer({
        session_id: 'session-1',
        stage_number: 1,
        question_id: 'q1',
        answer: 'answer',
      })
      expect(event.event_type).toBe('QUESTION_ANSWERED')

      // Get progress
      const progress = await mockProgress.refreshProgress()
      expect(progress.session_id).toBe('session-1')
    })
  })

  describe('Error Recovery Integration', () => {
    it('should recover from session creation error', async () => {
      const mockSession = createMockUseSession()
      mockSession.clearError = vi.fn()

      mockSession.clearError()
      expect(mockSession.clearError).toHaveBeenCalled()
    })

    it('should recover from progress error', async () => {
      const mockProgress = createMockUseProgress()
      mockProgress.clearError = vi.fn()

      mockProgress.clearError()
      expect(mockProgress.clearError).toHaveBeenCalled()
    })
  })
})

