/**
 * Global state management with Zustand.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ─── Types ───────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export interface Course {
  id: string;
  title: string;
  description?: string;
  created_at: string;
}

export interface Topic {
  id: string;
  title: string;
  description?: string;
  content?: string;
  difficulty: string;
  importance_score: number;
  status?: string;
  score?: number;
}

export interface Unit {
  id: string;
  title: string;
  description?: string;
  order_index: number;
  topics: Topic[];
}

// ─── Auth Store ──────────────────────────────────────────────────────────────

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: true }),
      setToken: (token) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', token);
        }
        set({ token, isAuthenticated: true });
      },
      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
        }
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    { name: 'auth-store' }
  )
);

// ─── Course Store ────────────────────────────────────────────────────────────

interface CourseState {
  courses: Course[];
  currentCourse: Course | null;
  units: Unit[];
  currentTopic: Topic | null;
  setCourses: (courses: Course[]) => void;
  setCurrentCourse: (course: Course | null) => void;
  setUnits: (units: Unit[]) => void;
  setCurrentTopic: (topic: Topic | null) => void;
}

export const useCourseStore = create<CourseState>((set) => ({
  courses: [],
  currentCourse: null,
  units: [],
  currentTopic: null,
  setCourses: (courses) => set({ courses }),
  setCurrentCourse: (currentCourse) => set({ currentCourse }),
  setUnits: (units) => set({ units }),
  setCurrentTopic: (currentTopic) => set({ currentTopic }),
}));

// ─── Learning Store ──────────────────────────────────────────────────────────

interface LearningState {
  progress: {
    total_topics: number;
    completed: number;
    in_progress: number;
    average_score: number;
  } | null;
  chatMessages: { role: string; content: string }[];
  setProgress: (progress: any) => void;
  addChatMessage: (message: { role: string; content: string }) => void;
  clearChat: () => void;
}

export const useLearningStore = create<LearningState>((set) => ({
  progress: null,
  chatMessages: [],
  setProgress: (progress) => set({ progress }),
  addChatMessage: (message) =>
    set((state) => ({ chatMessages: [...state.chatMessages, message] })),
  clearChat: () => set({ chatMessages: [] }),
}));
