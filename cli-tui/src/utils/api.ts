import axios, { AxiosInstance } from 'axios';
import type { Session } from '../state/store.js';

const API_BASE_URL = process.env.UAIP_API_URL || 'http://localhost:38937/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const message = error.response?.data?.detail || error.message || 'Unknown error occurred';
        throw new Error(message);
      }
    );
  }

  /**
   * Create a new session
   */
  async createSession(userId: string, projectName: string): Promise<Session> {
    const response = await this.client.post<Session>('/sessions/', {
      user_id: userId,
      project_name: projectName,
    });
    return response.data;
  }

  /**
   * Get session by ID
   */
  async getSession(sessionId: string): Promise<Session> {
    const response = await this.client.get<Session>(`/sessions/${sessionId}`);
    return response.data;
  }

  /**
   * Submit answer to current stage
   */
  async submitAnswer(
    sessionId: string,
    stage: number,
    questionId: string,
    answer: string
  ): Promise<{
    status: string;
    quality_score?: number;
    feedback?: string;
    needs_improvement?: boolean;
  }> {
    const response = await this.client.post(`/sessions/${sessionId}/stages/${stage}/answer`, {
      question_id: questionId,
      answer: answer,
    });
    return response.data;
  }

  /**
   * Advance to next stage
   */
  async advanceStage(sessionId: string): Promise<{
    session: Session;
    next_stage: number;
    message: string;
  }> {
    const response = await this.client.post(`/sessions/${sessionId}/advance`);
    return response.data;
  }

  /**
   * Run consistency check
   */
  async runConsistencyCheck(sessionId: string): Promise<{
    is_consistent: boolean;
    overall_feasibility: string;
    contradictions: string[];
    risk_areas: string[];
    recommendations: string[];
  }> {
    const response = await this.client.post(`/sessions/${sessionId}/consistency-check`);
    return response.data;
  }

  /**
   * Generate final charter
   */
  async generateCharter(sessionId: string): Promise<{
    charter: any;
    governance_decision: string;
    markdown_path?: string;
    pdf_path?: string;
  }> {
    const response = await this.client.post(`/sessions/${sessionId}/charter`);
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new ApiClient();
