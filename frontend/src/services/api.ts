/* API service layer */
const API_BASE = '/api';

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ---- Course API ----
export const courseAPI = {
  getAll: () => fetchAPI('/courses'),
  getById: (id: number) => fetchAPI(`/courses/${id}`),
  create: (data: any) => fetchAPI('/courses', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) => fetchAPI(`/courses/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) => fetchAPI(`/courses/${id}`, { method: 'DELETE' }),
};

// ---- Document API ----
export const documentAPI = {
  getAll: (courseId: number) => fetchAPI(`/documents/${courseId}`),
  upload: async (courseId: number, file: File, documentTag: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('course_id', courseId.toString());
    formData.append('document_tag', documentTag);
    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Upload failed');
    }
    return response.json();
  },
  delete: (courseId: number, docId: number) => fetchAPI(`/documents/${courseId}/${docId}`, { method: 'DELETE' }),
};

// ---- Chat API ----
export const chatAPI = {
  send: (data: { content: string; mode: string; course_id: number }) =>
    fetchAPI('/chat', { method: 'POST', body: JSON.stringify(data) }),
  
  stream: async function* (data: { content: string; mode: string; course_id: number }) {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) throw new Error('Chat stream failed');
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    if (!reader) throw new Error('No reader available');
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const text = decoder.decode(value);
      const lines = text.split('\\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.content) yield data.content;
            if (data.done) return;
          } catch {}
        }
      }
    }
  },
  
  getHistory: (courseId: number) => fetchAPI(`/chat/history/${courseId}`),
  clearHistory: (courseId: number) => fetchAPI(`/chat/history/${courseId}`, { method: 'DELETE' }),
};

// ---- Quiz API ----
export const quizAPI = {
  generate: (data: any) => fetchAPI('/quiz/generate', { method: 'POST', body: JSON.stringify(data) }),
  submit: (data: { quiz_id: number; answers: Record<string, string> }) =>
    fetchAPI('/quiz/submit', { method: 'POST', body: JSON.stringify(data) }),
  getAll: (courseId: number) => fetchAPI(`/quiz/${courseId}`),
  getById: (quizId: number) => fetchAPI(`/quiz/single/${quizId}`),
};

// ---- Revision API ----
export const revisionAPI = {
  generate: (data: { course_id: number; revision_type: string; topic?: string }) =>
    fetchAPI('/revision/generate', { method: 'POST', body: JSON.stringify(data) }),
  getAll: (courseId: number) => fetchAPI(`/revision/${courseId}`),
  generateFlashcards: (data: { course_id: number; topic?: string; num_cards?: number }) =>
    fetchAPI('/revision/flashcards/generate', { method: 'POST', body: JSON.stringify(data) }),
  getFlashcards: (courseId: number, dueOnly?: boolean) =>
    fetchAPI(`/revision/flashcards/${courseId}${dueOnly ? '?due_only=true' : ''}`),
  reviewFlashcard: (data: { flashcard_id: number; quality: number }) =>
    fetchAPI('/revision/flashcards/review', { method: 'POST', body: JSON.stringify(data) }),
};

// ---- Analytics API ----
export const analyticsAPI = {
  get: (courseId: number) => fetchAPI(`/analytics/${courseId}`),
  getProgress: (courseId: number) => fetchAPI(`/analytics/progress/${courseId}`),
};

// ---- Planner API ----
export const plannerAPI = {
  generate: (data: { course_id: number; hours_per_day: number; exam_date?: string }) =>
    fetchAPI('/planner/generate', { method: 'POST', body: JSON.stringify(data) }),
  startSession: (courseId: number, type: string) =>
    fetchAPI(`/planner/session/start?course_id=${courseId}&session_type=${type}`, { method: 'POST' }),
  endSession: (sessionId: number, topics?: string[]) =>
    fetchAPI(`/planner/session/end/${sessionId}`, { method: 'POST', body: JSON.stringify(topics || []) }),
};

// ---- Settings API ----
export const settingsAPI = {
  get: () => fetchAPI('/settings'),
  update: (data: any) => fetchAPI('/settings', { method: 'PUT', body: JSON.stringify(data) }),
  getProfile: () => fetchAPI('/settings/profile'),
  updateProfile: (data: any) => fetchAPI('/settings/profile', { method: 'PUT', body: JSON.stringify(data) }),
};
