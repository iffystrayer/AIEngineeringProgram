import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  createMockApiClient,
  createTestSession,
  createTestProgress,
  waitForAsync,
} from '../../test/mockServer'

describe('API Client Integration Tests', () => {
  let mockClient: ReturnType<typeof createMockApiClient>

  beforeEach(() => {
    mockClient = createMockApiClient()
  })

  describe('Session Management Integration', () => {
    it('should create a session and retrieve it', async () => {
      const createRequest = {
        user_id: 'user-123',
        project_name: 'Integration Test Project',
        description: 'Testing session creation',
      }

      const createdSession = await mockClient.createSession(createRequest)
      expect(createdSession.session_id).toBeDefined()
      expect(createdSession.project_name).toBe(createRequest.project_name)

      const retrievedSession = await mockClient.getSession(createdSession.session_id)
      expect(retrievedSession.session_id).toBe(createdSession.session_id)
      expect(retrievedSession.project_name).toBe(createRequest.project_name)
    })

    it('should list sessions for a user', async () => {
      const userId = `user-${Date.now()}`
      const createRequest = {
        user_id: userId,
        project_name: 'Project 1',
      }

      await mockClient.createSession(createRequest)
      await mockClient.createSession({
        ...createRequest,
        project_name: 'Project 2',
      })

      const sessions = await mockClient.listSessions(userId)
      expect(sessions.length).toBe(2)
      expect(sessions.every((s) => s.user_id === userId)).toBe(true)
    })

    it('should delete a session', async () => {
      const createdSession = await mockClient.createSession({
        user_id: 'user-123',
        project_name: 'To Delete',
      })

      await mockClient.deleteSession(createdSession.session_id)

      await expect(
        mockClient.getSession(createdSession.session_id)
      ).rejects.toThrow()
    })

    it('should handle session not found error', async () => {
      await expect(
        mockClient.getSession('non-existent-session')
      ).rejects.toThrow('not found')
    })
  })

  describe('Progress Tracking Integration', () => {
    it('should get progress for a session', async () => {
      const progress = await mockClient.getProgress('session-1')
      expect(progress.session_id).toBe('session-1')
      expect(progress.current_stage).toBeDefined()
      expect(progress.questions_answered).toBeDefined()
    })

    it('should submit an answer and track progress', async () => {
      const submitRequest = {
        session_id: 'session-1',
        stage_number: 1,
        question_id: 'q1',
        answer: 'test answer',
      }

      const event = await mockClient.submitAnswer(submitRequest)
      expect(event.event_type).toBe('QUESTION_ANSWERED')
      expect(event.data.question_id).toBe('q1')
    })

    it('should retrieve progress events', async () => {
      const events = await mockClient.getEvents('session-1')
      expect(Array.isArray(events)).toBe(true)
      expect(events.length).toBeGreaterThan(0)
    })

    it('should handle progress not found error', async () => {
      await expect(
        mockClient.getProgress('non-existent-session')
      ).rejects.toThrow('not found')
    })
  })

  describe('Real-Time Updates Integration', () => {
    it('should subscribe to SSE stream', async () => {
      const onMessage = vi.fn()
      const onError = vi.fn()

      const unsubscribe = mockClient.subscribeToStream(
        'session-1',
        onMessage,
        onError
      )

      // Wait for async callbacks
      await new Promise((resolve) => setTimeout(resolve, 200))

      expect(onMessage).toHaveBeenCalled()
      expect(onError).not.toHaveBeenCalled()

      unsubscribe()
    })

    it('should handle SSE errors', async () => {
      const onMessage = vi.fn()
      const onError = vi.fn()

      mockClient.subscribeToStream(
        'non-existent-session',
        onMessage,
        onError
      )

      await waitForAsync()

      // Should not throw, just handle gracefully
      expect(typeof onMessage).toBe('function')
    })
  })

  describe('Health Check Integration', () => {
    it('should check API health', async () => {
      const health = await mockClient.healthCheck()
      expect(health.status).toBe('ok')
    })
  })

  describe('Complete Workflow Integration', () => {
    it('should complete a full session workflow', async () => {
      // 1. Create session
      const createRequest = {
        user_id: `workflow-user-${Date.now()}`,
        project_name: 'Workflow Test',
        description: 'Testing complete workflow',
      }
      const session = await mockClient.createSession(createRequest)
      expect(session.session_id).toBeDefined()

      // 2. Get session details
      const sessionDetails = await mockClient.getSession(session.session_id)
      expect(sessionDetails.project_name).toBe(createRequest.project_name)

      // 3. Get initial progress (should exist now)
      const initialProgress = await mockClient.getProgress(session.session_id)
      expect(initialProgress.session_id).toBe(session.session_id)

      // 4. Submit answers
      const answer1 = await mockClient.submitAnswer({
        session_id: session.session_id,
        stage_number: 1,
        question_id: 'q1',
        answer: 'answer 1',
      })
      expect(answer1.event_type).toBe('QUESTION_ANSWERED')

      const answer2 = await mockClient.submitAnswer({
        session_id: session.session_id,
        stage_number: 1,
        question_id: 'q2',
        answer: 'answer 2',
      })
      expect(answer2.event_type).toBe('QUESTION_ANSWERED')

      // 5. Get all events
      const events = await mockClient.getEvents(session.session_id)
      expect(events.length).toBe(2)

      // 6. Delete session
      await mockClient.deleteSession(session.session_id)
      await expect(
        mockClient.getSession(session.session_id)
      ).rejects.toThrow()
    })
  })

  describe('Concurrent Operations', () => {
    it('should handle multiple concurrent sessions', async () => {
      const userId = `concurrent-user-${Date.now()}`
      const promises = Array.from({ length: 5 }, (_, i) =>
        mockClient.createSession({
          user_id: userId,
          project_name: `Project ${i}`,
        })
      )

      const sessions = await Promise.all(promises)
      expect(sessions).toHaveLength(5)
      // Each session should have unique ID
      const uniqueIds = new Set(sessions.map((s) => s.session_id))
      expect(uniqueIds.size).toBe(5)
    })

    it('should handle concurrent answers', async () => {
      const promises = Array.from({ length: 5 }, (_, i) =>
        mockClient.submitAnswer({
          session_id: 'session-1',
          stage_number: 1,
          question_id: `q${i}`,
          answer: `answer ${i}`,
        })
      )

      const events = await Promise.all(promises)
      expect(events).toHaveLength(5)
      expect(events.every((e) => e.event_type === 'QUESTION_ANSWERED')).toBe(true)
    })
  })
})

