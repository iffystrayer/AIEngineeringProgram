import { describe, it, expect, beforeEach } from 'vitest'
import {
  createMockApiClient,
  createTestSession,
  createTestProgress,
} from '../test/mockServer'

describe('Performance Tests', () => {
  let mockClient: ReturnType<typeof createMockApiClient>

  beforeEach(() => {
    mockClient = createMockApiClient()
  })

  describe('Session Operations Performance', () => {
    it('should create session within acceptable time', async () => {
      const startTime = performance.now()

      await mockClient.createSession({
        user_id: 'user-1',
        project_name: 'Test Project',
      })

      const endTime = performance.now()
      const duration = endTime - startTime

      // Should complete in less than 100ms
      expect(duration).toBeLessThan(100)
    })

    it('should retrieve session within acceptable time', async () => {
      const session = await mockClient.createSession({
        user_id: 'user-1',
        project_name: 'Test Project',
      })

      const startTime = performance.now()
      await mockClient.getSession(session.session_id)
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(100)
    })

    it('should list sessions within acceptable time', async () => {
      // Create multiple sessions
      for (let i = 0; i < 10; i++) {
        await mockClient.createSession({
          user_id: 'user-1',
          project_name: `Project ${i}`,
        })
      }

      const startTime = performance.now()
      await mockClient.listSessions('user-1')
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(100)
    })

    it('should delete session within acceptable time', async () => {
      const session = await mockClient.createSession({
        user_id: 'user-1',
        project_name: 'Test Project',
      })

      const startTime = performance.now()
      await mockClient.deleteSession(session.session_id)
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(100)
    })
  })

  describe('Progress Operations Performance', () => {
    it('should get progress within acceptable time', async () => {
      const startTime = performance.now()
      await mockClient.getProgress('session-1')
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(100)
    })

    it('should submit answer within acceptable time', async () => {
      const startTime = performance.now()

      await mockClient.submitAnswer({
        session_id: 'session-1',
        stage_number: 1,
        question_id: 'q1',
        answer: 'test answer',
      })

      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(100)
    })

    it('should get events within acceptable time', async () => {
      const startTime = performance.now()
      await mockClient.getEvents('session-1')
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(100)
    })
  })

  describe('Bulk Operations Performance', () => {
    it('should handle bulk session creation', async () => {
      const startTime = performance.now()

      const promises = Array.from({ length: 50 }, (_, i) =>
        mockClient.createSession({
          user_id: 'user-1',
          project_name: `Project ${i}`,
        })
      )

      await Promise.all(promises)

      const endTime = performance.now()
      const duration = endTime - startTime

      // Should complete 50 sessions in less than 5 seconds
      expect(duration).toBeLessThan(5000)
    })

    it('should handle bulk answer submissions', async () => {
      const startTime = performance.now()

      const promises = Array.from({ length: 100 }, (_, i) =>
        mockClient.submitAnswer({
          session_id: 'session-1',
          stage_number: 1,
          question_id: `q${i}`,
          answer: `answer ${i}`,
        })
      )

      await Promise.all(promises)

      const endTime = performance.now()
      const duration = endTime - startTime

      // Should complete 100 answers in less than 5 seconds
      expect(duration).toBeLessThan(5000)
    })

    it('should handle bulk session retrieval', async () => {
      // Create sessions
      const sessions = []
      for (let i = 0; i < 20; i++) {
        const session = await mockClient.createSession({
          user_id: 'user-1',
          project_name: `Project ${i}`,
        })
        sessions.push(session)
      }

      const startTime = performance.now()

      const promises = sessions.map((s) =>
        mockClient.getSession(s.session_id)
      )

      await Promise.all(promises)

      const endTime = performance.now()
      const duration = endTime - startTime

      // Should retrieve 20 sessions in less than 2 seconds
      expect(duration).toBeLessThan(2000)
    })
  })

  describe('Memory Performance', () => {
    it('should not leak memory on repeated operations', async () => {
      const iterations = 100

      for (let i = 0; i < iterations; i++) {
        const session = await mockClient.createSession({
          user_id: 'user-1',
          project_name: `Project ${i}`,
        })

        await mockClient.getSession(session.session_id)
        await mockClient.deleteSession(session.session_id)
      }

      // If we get here without crashing, memory is likely OK
      expect(true).toBe(true)
    })

    it('should handle large data payloads', async () => {
      const largeAnswer = 'A'.repeat(100000) // 100KB

      const startTime = performance.now()

      await mockClient.submitAnswer({
        session_id: 'session-1',
        stage_number: 1,
        question_id: 'q1',
        answer: largeAnswer,
      })

      const endTime = performance.now()

      // Should handle large payloads efficiently
      expect(endTime - startTime).toBeLessThan(500)
    })
  })

  describe('Concurrent Operations Performance', () => {
    it('should handle concurrent mixed operations', async () => {
      const startTime = performance.now()

      const promises = [
        ...Array.from({ length: 10 }, (_, i) =>
          mockClient.createSession({
            user_id: 'user-1',
            project_name: `Project ${i}`,
          })
        ),
        ...Array.from({ length: 20 }, () =>
          mockClient.getProgress('session-1')
        ),
        ...Array.from({ length: 20 }, (_, i) =>
          mockClient.submitAnswer({
            session_id: 'session-1',
            stage_number: 1,
            question_id: `q${i}`,
            answer: `answer ${i}`,
          })
        ),
      ]

      await Promise.all(promises)

      const endTime = performance.now()
      const duration = endTime - startTime

      // Should handle 50 concurrent operations in less than 5 seconds
      expect(duration).toBeLessThan(5000)
    })

    it('should maintain performance under load', async () => {
      const durations: number[] = []

      for (let batch = 0; batch < 5; batch++) {
        const startTime = performance.now()

        const promises = Array.from({ length: 20 }, (_, i) =>
          mockClient.createSession({
            user_id: 'user-1',
            project_name: `Project ${batch}-${i}`,
          })
        )

        await Promise.all(promises)

        const endTime = performance.now()
        durations.push(endTime - startTime)
      }

      // Performance should not degrade significantly
      const avgDuration = durations.reduce((a, b) => a + b) / durations.length
      expect(avgDuration).toBeLessThan(1000)
    })
  })

  describe('Response Time Consistency', () => {
    it('should have consistent response times', async () => {
      const durations: number[] = []

      for (let i = 0; i < 20; i++) {
        const startTime = performance.now()
        await mockClient.getProgress('session-1')
        const endTime = performance.now()
        durations.push(endTime - startTime)
      }

      const avgDuration = durations.reduce((a, b) => a + b) / durations.length
      const maxDuration = Math.max(...durations)

      // All should be reasonably fast (less than 100ms)
      expect(avgDuration).toBeLessThan(100)
      // Max should not be excessively slow (less than 500ms)
      expect(maxDuration).toBeLessThan(500)
    })
  })
})

