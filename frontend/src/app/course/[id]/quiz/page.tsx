'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import {
  ArrowLeft, Brain, Play, CheckCircle2, XCircle,
  Clock, Trophy, Loader2, RotateCcw
} from 'lucide-react';
import toast from 'react-hot-toast';
import { quizAPI, courseAPI } from '@/services/api';
import { Quiz, QuizQuestion } from '@/types';

export default function QuizPage() {
  const params = useParams();
  const courseId = Number(params.id);
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<any>(null);
  const [generating, setGenerating] = useState(false);
  const queryClient = useQueryClient();

  // Settings for quiz generation
  const [quizSettings, setQuizSettings] = useState({
    topic: '',
    quiz_type: 'mcq',
    difficulty: 'medium',
    num_questions: 5,
  });

  const { data: course } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => courseAPI.getById(courseId),
  });

  const { data: quizzes = [] } = useQuery({
    queryKey: ['quizzes', courseId],
    queryFn: () => quizAPI.getAll(courseId),
  });

  const generateQuiz = async () => {
    setGenerating(true);
    try {
      const quiz = await quizAPI.generate({ course_id: courseId, ...quizSettings });
      setActiveQuiz(quiz);
      setAnswers({});
      setResults(null);
      queryClient.invalidateQueries({ queryKey: ['quizzes', courseId] });
      toast.success('Quiz generated!');
    } catch (err) {
      toast.error('Failed to generate quiz. Check your API key.');
    } finally {
      setGenerating(false);
    }
  };

  const submitQuiz = async () => {
    if (!activeQuiz) return;
    try {
      const result = await quizAPI.submit({ quiz_id: activeQuiz.id, answers });
      setResults(result);
      queryClient.invalidateQueries({ queryKey: ['quizzes', courseId] });
      toast.success(`Score: ${result.score.toFixed(0)}%`);
    } catch (err) {
      toast.error('Failed to submit quiz');
    }
  };

  // If actively taking a quiz
  if (activeQuiz && !results) {
    return (
      <div className="min-h-screen bg-background">
        <header className="sticky top-0 z-50 glass border-b border-border">
          <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={() => setActiveQuiz(null)} className="p-2 rounded-xl hover:bg-secondary">
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h1 className="font-bold">{activeQuiz.title}</h1>
                <p className="text-xs text-muted-foreground">{activeQuiz.difficulty} • {activeQuiz.quiz_type.toUpperCase()}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="w-4 h-4" />
              {Math.floor(activeQuiz.time_limit / 60)} min
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-8 max-w-3xl">
          <div className="space-y-6">
            {activeQuiz.questions.map((q: QuizQuestion, idx: number) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="p-6 rounded-2xl bg-card border border-border"
              >
                <p className="font-medium mb-4">
                  <span className="text-primary mr-2">Q{idx + 1}.</span>
                  {q.question}
                </p>
                {q.options ? (
                  <div className="space-y-2">
                    {q.options.map((option, optIdx) => (
                      <button
                        key={optIdx}
                        onClick={() => setAnswers({ ...answers, [String(idx)]: option.charAt(0) })}
                        className={`w-full text-left p-3 rounded-xl border transition-all text-sm
                          ${answers[String(idx)] === option.charAt(0)
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-border hover:border-primary/30'}`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                ) : (
                  <input
                    type="text"
                    value={answers[String(idx)] || ''}
                    onChange={(e) => setAnswers({ ...answers, [String(idx)]: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="Type your answer..."
                  />
                )}
              </motion.div>
            ))}
          </div>

          <div className="mt-8 flex justify-end">
            <button
              onClick={submitQuiz}
              className="px-8 py-3 rounded-2xl bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
            >
              Submit Quiz
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Show results
  if (results) {
    return (
      <div className="min-h-screen bg-background">
        <header className="sticky top-0 z-50 glass border-b border-border">
          <div className="container mx-auto px-6 py-4 flex items-center gap-3">
            <button onClick={() => { setActiveQuiz(null); setResults(null); }} className="p-2 rounded-xl hover:bg-secondary">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="font-bold">Quiz Results</h1>
          </div>
        </header>

        <main className="container mx-auto px-6 py-8 max-w-3xl">
          {/* Score Card */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="p-8 rounded-2xl bg-card border border-border text-center mb-8"
          >
            <Trophy className={`w-12 h-12 mx-auto mb-4 ${results.score >= 70 ? 'text-yellow-500' : 'text-muted-foreground'}`} />
            <p className="text-4xl font-bold mb-2">{results.score.toFixed(0)}%</p>
            <p className="text-muted-foreground">
              {results.correct} / {results.total} correct
            </p>
          </motion.div>

          {/* Detailed Results */}
          <div className="space-y-4">
            {results.results.map((r: any, idx: number) => (
              <div key={idx} className={`p-4 rounded-xl border ${r.is_correct ? 'border-green-500/30 bg-green-500/5' : 'border-red-500/30 bg-red-500/5'}`}>
                <div className="flex items-start gap-3">
                  {r.is_correct ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className="font-medium text-sm mb-1">
                      Q{idx + 1}: {activeQuiz?.questions[idx]?.question}
                    </p>
                    {!r.is_correct && (
                      <p className="text-xs text-muted-foreground">
                        Correct answer: {r.correct_answer}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">{r.explanation}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 flex gap-3 justify-center">
            <button
              onClick={() => { setActiveQuiz(null); setResults(null); }}
              className="px-6 py-3 rounded-xl border border-border font-medium hover:bg-secondary transition-colors"
            >
              Back to Quizzes
            </button>
            <button
              onClick={() => { setResults(null); setAnswers({}); }}
              className="px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90"
            >
              <RotateCcw className="w-4 h-4 inline mr-2" /> Retry
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Default: Quiz list & generation
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 glass border-b border-border">
        <div className="container mx-auto px-6 py-4 flex items-center gap-3">
          <Link href={`/course/${courseId}`} className="p-2 rounded-xl hover:bg-secondary">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="font-bold">Quizzes</h1>
            <p className="text-xs text-muted-foreground">{course?.title}</p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-3xl">
        {/* Generate Quiz */}
        <div className="p-6 rounded-2xl bg-card border border-border mb-8">
          <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary" />
            Generate New Quiz
          </h2>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Topic (optional - leave empty for general quiz)"
              value={quizSettings.topic}
              onChange={(e) => setQuizSettings({ ...quizSettings, topic: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
            <div className="grid grid-cols-3 gap-3">
              <select
                value={quizSettings.quiz_type}
                onChange={(e) => setQuizSettings({ ...quizSettings, quiz_type: e.target.value })}
                className="px-3 py-2.5 rounded-xl bg-secondary border border-border text-sm"
              >
                <option value="mcq">MCQ</option>
                <option value="short_answer">Short Answer</option>
                <option value="numerical">Numerical</option>
              </select>
              <select
                value={quizSettings.difficulty}
                onChange={(e) => setQuizSettings({ ...quizSettings, difficulty: e.target.value })}
                className="px-3 py-2.5 rounded-xl bg-secondary border border-border text-sm"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
              <select
                value={quizSettings.num_questions}
                onChange={(e) => setQuizSettings({ ...quizSettings, num_questions: Number(e.target.value) })}
                className="px-3 py-2.5 rounded-xl bg-secondary border border-border text-sm"
              >
                <option value={5}>5 Questions</option>
                <option value={10}>10 Questions</option>
                <option value={15}>15 Questions</option>
                <option value={20}>20 Questions</option>
              </select>
            </div>
            <button
              onClick={generateQuiz}
              disabled={generating}
              className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {generating ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</>
              ) : (
                <><Play className="w-4 h-4" /> Generate & Start Quiz</>
              )}
            </button>
          </div>
        </div>

        {/* Previous Quizzes */}
        {quizzes.length > 0 && (
          <div>
            <h2 className="font-semibold text-lg mb-4">Previous Quizzes</h2>
            <div className="space-y-3">
              {quizzes.map((quiz: Quiz) => (
                <div
                  key={quiz.id}
                  className="p-4 rounded-xl bg-card border border-border flex items-center justify-between cursor-pointer hover:border-primary/30 transition-colors"
                  onClick={() => { setActiveQuiz(quiz); setAnswers({}); setResults(null); }}
                >
                  <div>
                    <p className="font-medium text-sm">{quiz.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {quiz.difficulty} • {quiz.questions.length} questions
                    </p>
                  </div>
                  <div className="text-right">
                    {quiz.is_completed ? (
                      <p className={`font-bold ${(quiz.score || 0) >= 70 ? 'text-green-500' : 'text-orange-500'}`}>
                        {quiz.score?.toFixed(0)}%
                      </p>
                    ) : (
                      <p className="text-xs text-muted-foreground">Not completed</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
