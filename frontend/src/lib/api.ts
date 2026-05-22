/**
 * API client for the AI Learning Engine backend.
 */
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// ─── Auth API ────────────────────────────────────────────────────────────────

export const authAPI = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  getMe: () => api.get('/auth/me'),
};

// ─── Ingestion API ───────────────────────────────────────────────────────────

export const ingestionAPI = {
  createCourse: (data: { title: string; description?: string }) =>
    api.post('/ingestion/courses', data),

  listCourses: () => api.get('/ingestion/courses'),

  uploadDocuments: (courseId: string, files: File[], docType: string) => {
    const formData = new FormData();
    formData.append('doc_type', docType);
    files.forEach((file) => formData.append('files', file));
    return api.post(`/ingestion/courses/${courseId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  processCourse: (courseId: string) =>
    api.post(`/ingestion/courses/${courseId}/process`),
};

// ─── Learning API ────────────────────────────────────────────────────────────

export const learningAPI = {
  getRoadmap: (courseId: string) =>
    api.get(`/learning/courses/${courseId}/roadmap`),

  getUnits: (courseId: string) =>
    api.get(`/learning/courses/${courseId}/units`),

  getTopicContent: (topicId: string) =>
    api.get(`/learning/topics/${topicId}`),

  markComplete: (topicId: string) =>
    api.post(`/learning/topics/${topicId}/complete`),

  getProgress: (courseId: string) =>
    api.get(`/learning/courses/${courseId}/progress`),

  getNextTopic: (courseId: string, currentTopicId?: string) =>
    api.get(`/learning/courses/${courseId}/next-topic`, {
      params: { current_topic_id: currentTopicId },
    }),
};

// ─── Quiz API ────────────────────────────────────────────────────────────────

export const quizAPI = {
  generateQuiz: (data: {
    topic_id: string;
    num_questions?: number;
    difficulty?: string;
    question_types?: string[];
  }) => api.post('/quiz/generate', data),

  getQuiz: (quizId: string) => api.get(`/quiz/${quizId}`),

  submitQuiz: (data: {
    quiz_id: string;
    answers: { question_id: string; answer: string }[];
    time_taken_seconds?: number;
  }) => api.post('/quiz/submit', data),

  getHistory: (courseId: string) => api.get(`/quiz/attempts/${courseId}`),
};

// ─── Adaptive API ────────────────────────────────────────────────────────────

export const adaptiveAPI = {
  askDoubt: (data: { message: string; topic_id?: string }) =>
    api.post('/adaptive/doubt', data),

  getRecommendation: (courseId: string) =>
    api.get(`/adaptive/recommend/${courseId}`),

  getAnalytics: (courseId: string) =>
    api.get(`/adaptive/analytics/${courseId}`),
};

export default api;
