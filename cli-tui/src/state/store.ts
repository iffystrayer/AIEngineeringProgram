import { create } from 'zustand';

// Types matching backend API
export interface Session {
  session_id: string;
  user_id: string;
  project_name: string;
  current_stage: number;
  status: 'in_progress' | 'completed' | 'abandoned' | 'paused';
  started_at: string;
  last_updated_at: string;
}

export interface Question {
  id: string;
  text: string;
  placeholder?: string;
  multiline?: boolean;
}

export interface Answer {
  questionId: string;
  text: string;
  qualityScore?: number;
  feedback?: string;
}

export interface AppState {
  // Session data
  session: Session | null;
  currentQuestion: Question | null;
  answers: Answer[];

  // UI state
  isLoading: boolean;
  isProcessing: boolean;
  error: string | null;
  currentView: 'welcome' | 'session-start' | 'question' | 'quality-feedback' | 'stage-complete' | 'final-complete';

  // Progress tracking
  totalStages: number;
  currentStage: number;
  stageProgress: number; // 0-100

  // Actions
  setSession: (session: Session) => void;
  setCurrentQuestion: (question: Question | null) => void;
  addAnswer: (answer: Answer) => void;
  setLoading: (loading: boolean) => void;
  setProcessing: (processing: boolean) => void;
  setError: (error: string | null) => void;
  setCurrentView: (view: AppState['currentView']) => void;
  setStageProgress: (progress: number) => void;
  reset: () => void;
}

const initialState = {
  session: null,
  currentQuestion: null,
  answers: [],
  isLoading: false,
  isProcessing: false,
  error: null,
  currentView: 'welcome' as const,
  totalStages: 5,
  currentStage: 1,
  stageProgress: 0,
};

export const useStore = create<AppState>((set) => ({
  ...initialState,

  setSession: (session) =>
    set({
      session,
      currentStage: session.current_stage
    }),

  setCurrentQuestion: (question) =>
    set({ currentQuestion: question }),

  addAnswer: (answer) =>
    set((state) => ({
      answers: [...state.answers, answer]
    })),

  setLoading: (loading) =>
    set({ isLoading: loading }),

  setProcessing: (processing) =>
    set({ isProcessing: processing }),

  setError: (error) =>
    set({ error }),

  setCurrentView: (view) =>
    set({ currentView: view }),

  setStageProgress: (progress) =>
    set({ stageProgress: progress }),

  reset: () =>
    set(initialState),
}));
