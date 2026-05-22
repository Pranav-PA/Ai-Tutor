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
