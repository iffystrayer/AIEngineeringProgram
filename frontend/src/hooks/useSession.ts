/**
 * useSession Hook
 * Manages session state and operations
 */

import { useState, useCallback } from 'react'
import type { SessionResponse } from '../services/api'
import {
  createSession,
  getSession,
  listSessions,
  deleteSession,
} from '../services/api'

export interface UseSessionState {
  session: SessionResponse | null;
  sessions: SessionResponse[];
  sessionId: string | null;
  status: string | null;
  isLoading: boolean;
  error: Error | null;
  createNewSession: (
    userId: string,
    projectName: string,
    description?: string
  ) => Promise<SessionResponse>;
  getSessionDetails: (sessionId: string) => Promise<SessionResponse>;
  listUserSessions: (userId: string) => Promise<SessionResponse[]>;
  deleteCurrentSession: (sessionId: string) => Promise<void>;
  clearError: () => void;
}

/**
 * Hook for managing session state and operations
 */
export function useSession(): UseSessionState {
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [sessions, setSessions] = useState<SessionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Create a new session
  const createNewSession = useCallback(
    async (
      userId: string,
      projectName: string,
      description?: string
    ): Promise<SessionResponse> => {
      setIsLoading(true);
      setError(null);

      try {
        const newSession = await createSession({
          user_id: userId,
          project_name: projectName,
          description,
        });

        setSession(newSession);
        return newSession;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Get session details
  const getSessionDetails = useCallback(
    async (sessionId: string): Promise<SessionResponse> => {
      setIsLoading(true);
      setError(null);

      try {
        const sessionData = await getSession(sessionId);
        setSession(sessionData);
        return sessionData;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // List user sessions
  const listUserSessions = useCallback(
    async (userId: string): Promise<SessionResponse[]> => {
      setIsLoading(true);
      setError(null);

      try {
        const userSessions = await listSessions(userId);
        setSessions(userSessions);
        return userSessions;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Delete a session
  const deleteCurrentSession = useCallback(
    async (sessionId: string): Promise<void> => {
      setIsLoading(true);
      setError(null);

      try {
        await deleteSession(sessionId);

        // Clear session if it's the current one
        if (session?.session_id === sessionId) {
          setSession(null);
        }

        // Remove from sessions list
        setSessions((prev) =>
          prev.filter((s) => s.session_id !== sessionId)
        );
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [session]
  );

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    session,
    sessions,
    sessionId: session?.session_id || null,
    status: session?.status || null,
    isLoading,
    error,
    createNewSession,
    getSessionDetails,
    listUserSessions,
    deleteCurrentSession,
    clearError,
  };
}

