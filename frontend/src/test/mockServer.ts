import { vi } from 'vitest'
import type { SessionResponse, ProgressResponse, ProgressEvent } from '../services/api'

/**
 * Mock Server Setup for Testing
 * 
 * Provides mock implementations of API endpoints for testing
 * without requiring a real backend server.
 */

// Mock data
export const mockSessions: Record<string, SessionResponse> = {
  'session-1': {
    session_id: 'session-1',
    user_id: 'user-1',
    project_name: 'Test Project 1',
    description: 'First test project',
    status: 'in_progress',
    created_at: '2025-10-20T10:00:00Z',
    started_at: '2025-10-20T10:05:00Z',
  },
  'session-2': {
    session_id: 'session-2',
    user_id: 'user-1',
    project_name: 'Test Project 2',
    description: 'Second test project',
    status: 'completed',
    created_at: '2025-10-19T10:00:00Z',
    started_at: '2025-10-19T10:05:00Z',
  },
}

export const mockProgress: ProgressResponse = {
  session_id: 'session-1',
  current_stage: 2,
  questions_answered: 5,
  charter_status: 'generating',
  total_questions: 20,
  started_at: '2025-10-20T10:05:00Z',
}

export const mockProgressEvents: ProgressEvent[] = [
  {
    event_id: 'event-1',
    session_id: 'session-1',
    event_type: 'STAGE_STARTED',
    stage_number: 1,
    timestamp: '2025-10-20T10:05:00Z',
    data: { stage: 1 },
  },
  {
    event_id: 'event-2',
    session_id: 'session-1',
    event_type: 'QUESTION_ANSWERED',
    stage_number: 1,
    timestamp: '2025-10-20T10:06:00Z',
    data: { question_id: 'q1', answer: 'test answer' },
  },
]

/**
 * Mock API Client
 * Simulates API responses for testing
 */
export const createMockApiClient = () => {
  const sessions = new Map(Object.entries(mockSessions))
  const events = new Map<string, ProgressEvent[]>([
    ['session-1', mockProgressEvents],
  ])
  const progress = new Map<string, ProgressResponse>([
    ['session-1', mockProgress],
  ])
  let sessionCounter = 0

  return {
    // Session Management
    createSession: vi.fn(async (request) => {
      const newSession: SessionResponse = {
        session_id: `session-${Date.now()}-${sessionCounter++}`,
        user_id: request.user_id,
        project_name: request.project_name,
        description: request.description,
        status: 'in_progress',
        created_at: new Date().toISOString(),
      }
      sessions.set(newSession.session_id, newSession)

      // Create initial progress for new session
      progress.set(newSession.session_id, {
        session_id: newSession.session_id,
        current_stage: 1,
        questions_answered: 0,
        charter_status: 'pending',
        total_questions: 20,
        started_at: new Date().toISOString(),
      })

      // Create initial events array
      events.set(newSession.session_id, [])

      return newSession
    }),

    getSession: vi.fn(async (sessionId: string) => {
      const session = sessions.get(sessionId)
      if (!session) {
        throw new Error(`Session ${sessionId} not found`)
      }
      return session
    }),

    listSessions: vi.fn(async (userId: string) => {
      return Array.from(sessions.values()).filter(
        (s) => s.user_id === userId
      )
    }),

    deleteSession: vi.fn(async (sessionId: string) => {
      sessions.delete(sessionId)
      events.delete(sessionId)
      progress.delete(sessionId)
    }),

    // Progress Tracking
    getProgress: vi.fn(async (sessionId: string) => {
      const sessionProgress = progress.get(sessionId)
      if (!sessionProgress) {
        throw new Error(`Progress for session ${sessionId} not found`)
      }
      return sessionProgress
    }),

    submitAnswer: vi.fn(async (request) => {
      const event: ProgressEvent = {
        event_id: `event-${Date.now()}`,
        session_id: request.session_id,
        event_type: 'QUESTION_ANSWERED',
        stage_number: request.stage_number,
        timestamp: new Date().toISOString(),
        data: { question_id: request.question_id, answer: request.answer },
      }
      const sessionEvents = events.get(request.session_id) || []
      sessionEvents.push(event)
      events.set(request.session_id, sessionEvents)
      return event
    }),

    getEvents: vi.fn(async (sessionId: string) => {
      return events.get(sessionId) || []
    }),

    subscribeToStream: vi.fn((sessionId: string, onMessage, onError) => {
      // Simulate SSE subscription with immediate callback
      const sessionEvents = events.get(sessionId) || []
      if (sessionEvents.length > 0) {
        sessionEvents.forEach((event, index) => {
          setTimeout(() => onMessage(event), index * 50)
        })
      } else {
        // Send at least one event to indicate stream is active
        setTimeout(() => {
          onMessage({
            event_id: `stream-event-${Date.now()}`,
            session_id: sessionId,
            event_type: 'STREAM_STARTED',
            stage_number: 1,
            timestamp: new Date().toISOString(),
            data: {},
          })
        }, 10)
      }
      return () => {
        // Cleanup
      }
    }),

    healthCheck: vi.fn(async () => {
      return { status: 'ok' }
    }),
  }
}

/**
 * Mock Hook Implementations
 */
export const createMockUseSession = () => ({
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
})

export const createMockUseProgress = () => ({
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
})

/**
 * Test Utilities
 */
export const waitForAsync = () => new Promise((resolve) => setTimeout(resolve, 0))

export const createTestSession = (overrides?: Partial<SessionResponse>): SessionResponse => ({
  session_id: 'test-session',
  user_id: 'test-user',
  project_name: 'Test Project',
  description: 'Test Description',
  status: 'in_progress',
  created_at: new Date().toISOString(),
  ...overrides,
})

export const createTestProgress = (overrides?: Partial<ProgressResponse>): ProgressResponse => ({
  session_id: 'test-session',
  current_stage: 1,
  questions_answered: 0,
  charter_status: 'pending',
  total_questions: 20,
  started_at: new Date().toISOString(),
  ...overrides,
})

export const createTestProgressEvent = (overrides?: Partial<ProgressEvent>): ProgressEvent => ({
  event_id: 'test-event',
  session_id: 'test-session',
  event_type: 'QUESTION_ANSWERED',
  stage_number: 1,
  timestamp: new Date().toISOString(),
  data: {},
  ...overrides,
})

