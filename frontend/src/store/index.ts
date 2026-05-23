import { create } from 'zustand';
import { Course, Settings, UserProfile } from '@/types';

interface AppState {
  // User
  user: UserProfile | null;
  setUser: (user: UserProfile) => void;

  // Courses
  courses: Course[];
  setCourses: (courses: Course[]) => void;
  addCourse: (course: Course) => void;
  removeCourse: (id: number) => void;
  updateCourse: (id: number, data: Partial<Course>) => void;

  // Active course
  activeCourse: Course | null;
  setActiveCourse: (course: Course | null) => void;

  // Settings
  settings: Settings | null;
  setSettings: (settings: Settings) => void;

  // UI State
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  commandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // User
  user: null,
  setUser: (user) => set({ user }),

  // Courses
  courses: [],
  setCourses: (courses) => set({ courses }),
  addCourse: (course) => set((state) => ({ courses: [course, ...state.courses] })),
  removeCourse: (id) => set((state) => ({ courses: state.courses.filter((c) => c.id !== id) })),
  updateCourse: (id, data) =>
    set((state) => ({
      courses: state.courses.map((c) => (c.id === id ? { ...c, ...data } : c)),
    })),

  // Active course
  activeCourse: null,
  setActiveCourse: (course) => set({ activeCourse: course }),

  // Settings
  settings: null,
  setSettings: (settings) => set({ settings }),

  // UI
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  commandPaletteOpen: false,
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
}));

// ---- Auth Store ----
interface AuthState {
  user: any | null;
  token: string | null;
  setUser: (user: any) => void;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('access_token') : null,
  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
    set({ token });
  },
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
    set({ user: null, token: null });
  },
}));

// ---- Course Store ----
interface CourseState {
  currentCourse: any | null;
  currentTopic: any | null;
  setCurrentCourse: (course: any) => void;
  setCurrentTopic: (topic: any | null) => void;
}

export const useCourseStore = create<CourseState>((set) => ({
  currentCourse: null,
  currentTopic: null,
  setCurrentCourse: (course) => set({ currentCourse: course }),
  setCurrentTopic: (topic) => set({ currentTopic: topic }),
}));

// ---- Learning Store ----
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface LearningState {
  chatMessages: ChatMessage[];
  addChatMessage: (message: ChatMessage) => void;
  clearChat: () => void;
}

export const useLearningStore = create<LearningState>((set) => ({
  chatMessages: [],
  addChatMessage: (message) => set((state) => ({ chatMessages: [...state.chatMessages, message] })),
  clearChat: () => set({ chatMessages: [] }),
}));
