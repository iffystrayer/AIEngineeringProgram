/**
 * API Client Service
 * Handles all communication with the backend API
 */

import axios from 'axios'
import type { AxiosError } from 'axios'

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:38937/api/v1';
const API_TIMEOUT = 30000; // 30 seconds

// ============================================================================
// Axios Instance
// ============================================================================

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================================================
// Type Definitions
// ============================================================================

export interface CreateSessionRequest {
  user_id: string;
  project_name: string;
  description?: string;
}

export interface SessionResponse {
  session_id: string;
  user_id: string;
  project_name: string;
  description?: string;
  status: string;
  created_at?: string;
  started_at?: string;
}

export interface SubmitAnswerRequest {
  stage_number: number;
  question_id: string;
  answer: string;
  quality_score: number;
}

export interface ProgressResponse {
  session_id: string;
  status: string;
  current_stage: number;
  questions_answered: number;
  charter_status: string;
}

export interface ProgressEvent {
  event_id: string;
  session_id: string;
  event_type: string;
  timestamp: string;
  data: Record<string, unknown>;
}

// ============================================================================
// Session Management
// ============================================================================

/**
 * Create a new session
 */
export async function createSession(
  request: CreateSessionRequest
): Promise<SessionResponse> {
  try {
    const response = await apiClient.post<SessionResponse>(
      '/api/sessions',
      request
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Get session details
 */
export async function getSession(sessionId: string): Promise<SessionResponse> {
  try {
    const response = await apiClient.get<SessionResponse>(
      `/api/sessions/${sessionId}`
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * List sessions for a user
 */
export async function listSessions(userId: string): Promise<SessionResponse[]> {
  try {
    const response = await apiClient.get<SessionResponse[]>(
      '/api/sessions',
      {
        params: { user_id: userId },
      }
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Delete a session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  try {
    await apiClient.delete(`/api/sessions/${sessionId}`);
  } catch (error) {
    throw handleApiError(error);
  }
}

// ============================================================================
// Progress Tracking
// ============================================================================

/**
 * Get session progress
 */
export async function getProgress(
  sessionId: string
): Promise<ProgressResponse> {
  try {
    const response = await apiClient.get<ProgressResponse>(
      `/api/sessions/${sessionId}/progress`
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Submit an answer
 */
export async function submitAnswer(
  sessionId: string,
  request: SubmitAnswerRequest
): Promise<{ status: string; session_id: string }> {
  try {
    const response = await apiClient.post(
      `/api/sessions/${sessionId}/answer`,
      request
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Get progress events
 */
export async function getEvents(sessionId: string): Promise<ProgressEvent[]> {
  try {
    const response = await apiClient.get<ProgressEvent[]>(
      `/api/sessions/${sessionId}/events`
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

// ============================================================================
// Real-Time Updates (SSE)
// ============================================================================

/**
 * Subscribe to real-time progress updates via SSE
 */
export function subscribeToStream(
  sessionId: string,
  onMessage: (event: ProgressEvent) => void,
  onError: (error: Error) => void
): () => void {
  const eventSource = new EventSource(
    `${API_BASE_URL}/api/sessions/${sessionId}/stream`
  );

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      onError(new Error(`Failed to parse SSE message: ${error}`));
    }
  };

  eventSource.onerror = () => {
    onError(new Error('SSE connection error'));
    eventSource.close();
  };

  // Return unsubscribe function
  return () => {
    eventSource.close();
  };
}

// ============================================================================
// Error Handling
// ============================================================================

interface ApiErrorResponse {
  detail?: string;
  message?: string;
}

export class ApiError extends Error {
  status: number
  data?: unknown

  constructor(status: number, message: string, data?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

/**
 * Handle API errors
 */
function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;
    const status = axiosError.response?.status || 500;
    const message =
      axiosError.response?.data?.detail ||
      axiosError.response?.data?.message ||
      axiosError.message ||
      'Unknown error';

    return new ApiError(status, message, axiosError.response?.data);
  }

  if (error instanceof Error) {
    return new ApiError(500, error.message);
  }

  return new ApiError(500, 'Unknown error occurred');
}

// ============================================================================
// Health Check
// ============================================================================

/**
 * Check API health
 */
export async function healthCheck(): Promise<{ status: string }> {
  try {
    const response = await apiClient.get<{ status: string }>('/health');
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

