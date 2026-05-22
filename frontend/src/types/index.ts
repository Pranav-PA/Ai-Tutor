/* Types for the AI Semester Companion */

export interface Course {
  id: number;
  title: string;
  semester?: string;
  university?: string;
  subject?: string;
  exam_date?: string;
  color: string;
  icon: string;
  is_archived: boolean;
  created_at: string;
  document_count: number;
  quiz_count: number;
  progress_percentage: number;
}

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  is_processed: boolean;
  document_tag?: string;
  uploaded_at: string;
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  mode: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface Quiz {
  id: number;
  title: string;
  quiz_type: string;
  difficulty: string;
  questions: QuizQuestion[];
  score: number | null;
  total_marks: number;
  time_limit: number;
  is_completed: boolean;
  created_at: string;
}

export interface QuizQuestion {
  id?: number;
  question: string;
  type?: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
  difficulty?: string;
  topic?: string;
  marks?: number;
}

export interface Flashcard {
  id: number;
  question: string;
  answer: string;
  topic?: string;
  difficulty: string;
  review_interval: number;
  next_review?: string;
  repetitions: number;
}

export interface Progress {
  id: number;
  topic: string;
  unit?: string;
  confidence: number;
  times_studied: number;
  times_quizzed: number;
  quiz_accuracy: number;
  is_weak: boolean;
  last_studied?: string;
}

export interface Analytics {
  syllabus_completion: number;
  quiz_accuracy: number;
  weak_topics: string[];
  strong_topics: string[];
  total_study_hours: number;
  revision_streak: number;
  ai_readiness_score: number;
  topics_by_confidence: Array<{ topic: string; confidence: number; is_weak: boolean }>;
  quiz_history: Array<{ date: string; score: number; type: string; difficulty: string }>;
  study_sessions: Array<{ date: string; duration: number; type: string }>;
}

export interface RevisionContent {
  id: number;
  topic: string;
  revision_type: string;
  content: string;
  created_at: string;
}

export interface StudyPlan {
  course_id: number;
  schedule: Array<{
    day: number;
    date: string;
    topics: string[];
    hours: number;
    type: string;
    tips?: string;
  }>;
  revision_dates: string[];
  mock_test_dates: string[];
}

export interface Settings {
  has_openai_key: boolean;
  has_gemini_key: boolean;
  preferred_provider: string;
  theme: string;
}

export interface UserProfile {
  id: number;
  name: string;
  learning_style: string;
  preferred_provider: string;
  created_at: string;
}
