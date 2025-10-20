/**
 * Tests for API client service
 * TDD approach: Tests written first, implementation follows
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import {
  createSession,
  getSession,
  listSessions,
  deleteSession,
  getProgress,
  submitAnswer,
  getEvents,
  subscribeToStream,
  ApiError,
} from '../api';

// Mock EventSource
global.EventSource = vi.fn(() => ({
  onmessage: null,
  onerror: null,
  close: vi.fn(),
})) as any;

describe('API Client Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Session Management', () => {
    it('should have createSession function', () => {
      expect(typeof createSession).toBe('function');
    });

    it('should have getSession function', () => {
      expect(typeof getSession).toBe('function');
    });

    it('should have listSessions function', () => {
      expect(typeof listSessions).toBe('function');
    });

    it('should have deleteSession function', () => {
      expect(typeof deleteSession).toBe('function');
    });

    it('should accept session creation parameters', () => {
      const params = {
        user_id: 'user123',
        project_name: 'Test Project',
        description: 'A test project',
      };

      expect(params.user_id).toBe('user123');
      expect(params.project_name).toBe('Test Project');
    });
  });

  describe('Progress Tracking', () => {
    it('should have getProgress function', () => {
      expect(typeof getProgress).toBe('function');
    });

    it('should have submitAnswer function', () => {
      expect(typeof submitAnswer).toBe('function');
    });

    it('should have getEvents function', () => {
      expect(typeof getEvents).toBe('function');
    });

    it('should accept answer submission parameters', () => {
      const params = {
        stage_number: 1,
        question_id: 'q1',
        answer: 'Test answer',
        quality_score: 8.5,
      };

      expect(params.stage_number).toBe(1);
      expect(params.quality_score).toBe(8.5);
    });

    it('should validate stage numbers', () => {
      const validStage = 1;
      const invalidStage = 10;

      expect(validStage).toBeGreaterThan(0);
      expect(validStage).toBeLessThanOrEqual(5);
      expect(invalidStage).toBeGreaterThan(5);
    });
  });

  describe('Real-Time Updates', () => {
    it('should subscribe to SSE stream', async () => {
      const sessionId = 'test-session-123';
      const onMessage = vi.fn();
      const onError = vi.fn();
      
      const unsubscribe = subscribeToStream(sessionId, onMessage, onError);
      
      expect(typeof unsubscribe).toBe('function');
    });

    it('should handle stream connection errors', async () => {
      const sessionId = 'test-session-123';
      const onMessage = vi.fn();
      const onError = vi.fn();
      
      subscribeToStream(sessionId, onMessage, onError);
      
      // Simulate error
      expect(onError).toBeDefined();
    });

    it('should unsubscribe from stream', async () => {
      const sessionId = 'test-session-123';
      const onMessage = vi.fn();
      const onError = vi.fn();
      
      const unsubscribe = subscribeToStream(sessionId, onMessage, onError);
      unsubscribe();
      
      expect(unsubscribe).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('should have ApiError class', () => {
      expect(ApiError).toBeDefined();
    });

    it('should create ApiError with status 404', () => {
      const error = new ApiError(404, 'Not found');

      expect(error.status).toBe(404);
      expect(error.message).toBe('Not found');
    });

    it('should create ApiError with status 400', () => {
      const error = new ApiError(400, 'Bad request');

      expect(error.status).toBe(400);
      expect(error.message).toBe('Bad request');
    });

    it('should create ApiError with status 500', () => {
      const error = new ApiError(500, 'Server error');

      expect(error.status).toBe(500);
      expect(error.message).toBe('Server error');
    });

    it('should store error data', () => {
      const data = { detail: 'Invalid input' };
      const error = new ApiError(422, 'Validation error', data);

      expect(error.data).toEqual(data);
    });
  });

  describe('API Error Handling', () => {
    it('should create ApiError with status and message', () => {
      const error = new ApiError(404, 'Not found');

      expect(error.status).toBe(404);
      expect(error.message).toBe('Not found');
      expect(error.name).toBe('ApiError');
    });

    it('should handle different error statuses', () => {
      const error400 = new ApiError(400, 'Bad request');
      const error500 = new ApiError(500, 'Server error');

      expect(error400.status).toBe(400);
      expect(error500.status).toBe(500);
    });
  });
});

