/**
 * useProgress Hook
 * Manages progress tracking and real-time updates
 */

import { useState, useCallback, useEffect } from 'react';
import {
  getProgress,
  getEvents,
  submitAnswer,
  subscribeToStream,
  ProgressResponse,
  ProgressEvent,
  SubmitAnswerRequest,
} from '../services/api';

export interface UseProgressState {
  progress: ProgressResponse | null;
  events: ProgressEvent[];
  currentStage: number | null;
  questionsAnswered: number | null;
  charterStatus: string | null;
  isLoading: boolean;
  error: Error | null;
  submitAnswer: (request: SubmitAnswerRequest) => Promise<void>;
  refreshProgress: () => Promise<void>;
  clearError: () => void;
}

/**
 * Hook for managing progress tracking
 */
export function useProgress(sessionId: string): UseProgressState {
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Fetch progress
  const fetchProgress = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [progressData, eventsData] = await Promise.all([
        getProgress(sessionId),
        getEvents(sessionId),
      ]);

      setProgress(progressData);
      setEvents(eventsData);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  // Fetch progress on mount and when sessionId changes
  useEffect(() => {
    fetchProgress();
  }, [sessionId, fetchProgress]);

  // Subscribe to real-time updates
  useEffect(() => {
    let unsubscribe: (() => void) | null = null;

    try {
      unsubscribe = subscribeToStream(
        sessionId,
        (event: ProgressEvent) => {
          // Add new event to the list
          setEvents((prev) => [...prev, event]);

          // Update progress if it's a progress update event
          if (event.event_type === 'PROGRESS_UPDATE') {
            setProgress((prev) =>
              prev
                ? {
                    ...prev,
                    ...event.data,
                  }
                : null
            );
          }
        },
        (err: Error) => {
          setError(err);
        }
      );
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
    }

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, [sessionId]);

  // Submit answer
  const submitAnswerFn = useCallback(
    async (request: SubmitAnswerRequest): Promise<void> => {
      setIsLoading(true);
      setError(null);

      try {
        await submitAnswer(sessionId, request);
        // Refresh progress after submission
        await fetchProgress();
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, fetchProgress]
  );

  // Refresh progress
  const refreshProgress = useCallback(async () => {
    await fetchProgress();
  }, [fetchProgress]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    progress,
    events,
    currentStage: progress?.current_stage || null,
    questionsAnswered: progress?.questions_answered || null,
    charterStatus: progress?.charter_status || null,
    isLoading,
    error,
    submitAnswer: submitAnswerFn,
    refreshProgress,
    clearError,
  };
}

