'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { quizAPI } from '@/lib/api';
import { useCourseStore } from '@/store';
import { FiCheck, FiX, FiClock, FiAward } from 'react-icons/fi';

interface Question {
  id: string;
  question_type: string;
  question_text: string;
  options?: string[];
  points: number;
  order_index: number;
}

interface QuizData {
  id: string;
  title: string;
  difficulty: string;
  questions: Question[];
}

export default function QuizPage() {
  const { currentTopic } = useCourseStore();
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [startTime] = useState(Date.now());

  const handleGenerateQuiz = async () => {
    if (!currentTopic?.id) {
      toast.error('Select a topic first from the Learning page');
      return;
    }
    setGenerating(true);
    try {
      const res = await quizAPI.generateQuiz({
        topic_id: currentTopic.id,
        num_questions: 5,
        difficulty: 'intermediate',
        question_types: ['mcq', 'short_answer'],
      });
      setQuiz(res.data);
      setAnswers({});
      setResult(null);
      setCurrentQuestion(0);
    } catch (error) {
      toast.error('Failed to generate quiz');
    } finally {
      setGenerating(false);
    }
  };

  const handleSubmit = async () => {
    if (!quiz) return;
    setLoading(true);
    try {
      const timeTaken = Math.floor((Date.now() - startTime) / 1000);
      const res = await quizAPI.submitQuiz({
        quiz_id: quiz.id,
        answers: Object.entries(answers).map(([qId, answer]) => ({
          question_id: qId,
          answer,
        })),
        time_taken_seconds: timeTaken,
      });
      setResult(res.data);
      toast.success('Quiz submitted!');
    } catch (error) {
      toast.error('Failed to submit quiz');
    } finally {
      setLoading(false);
    }
  };

  // No quiz generated yet
  if (!quiz) {
    return (
      <div className="max-w-2xl mx-auto text-center py-20">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <span className="text-6xl block mb-6">📝</span>
          <h1 className="text-3xl font-bold text-dark-50 mb-4">Ready for a Quiz?</h1>
          <p className="text-dark-400 mb-8">
            {currentTopic
              ? `Generate a quiz for "${currentTopic.title}"`
              : 'Select a topic from the Learning page first'}
          </p>
          <button
            onClick={handleGenerateQuiz}
            disabled={generating || !currentTopic}
            className="btn-primary text-lg px-8 py-3 disabled:opacity-50"
          >
            {generating ? 'Generating...' : 'Generate Quiz'}
          </button>
        </motion.div>
      </div>
    );
  }

  // Show results
  if (result) {
    return (
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card text-center mb-8"
        >
          <span className="text-5xl block mb-4">
            {result.percentage >= 80 ? '🎉' : result.percentage >= 60 ? '👍' : '📚'}
          </span>
          <h2 className="text-2xl font-bold text-dark-50 mb-2">Quiz Complete!</h2>
          <div className="flex justify-center gap-8 mt-6">
            <div>
              <p className="text-3xl font-bold text-primary-400">{result.percentage}%</p>
              <p className="text-dark-400 text-sm">Score</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-dark-200">
                {result.score}/{result.max_score}
              </p>
              <p className="text-dark-400 text-sm">Points</p>
            </div>
          </div>
        </motion.div>

        {/* Detailed feedback */}
        <div className="space-y-4">
          {(result.feedback || []).map((item: any, i: number) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`card border-l-4 ${
                item.is_correct ? 'border-l-green-500' : 'border-l-red-500'
              }`}
            >
              <div className="flex items-start gap-3">
                {item.is_correct ? (
                  <FiCheck className="w-5 h-5 text-green-400 mt-1" />
                ) : (
                  <FiX className="w-5 h-5 text-red-400 mt-1" />
                )}
                <div className="flex-1">
                  <p className="text-dark-200 font-medium">{item.question}</p>
                  <p className="text-sm text-dark-400 mt-1">
                    Your answer: <span className="text-dark-300">{item.user_answer || '(no answer)'}</span>
                  </p>
                  {!item.is_correct && (
                    <p className="text-sm text-green-400 mt-1">
                      Correct: {item.correct_answer}
                    </p>
                  )}
                  {item.feedback && (
                    <p className="text-xs text-dark-500 mt-2">{item.feedback}</p>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="flex justify-center gap-4 mt-8">
          <button onClick={handleGenerateQuiz} className="btn-secondary">
            Try Again
          </button>
          <button onClick={() => { setQuiz(null); setResult(null); }} className="btn-primary">
            New Quiz
          </button>
        </div>
      </div>
    );
  }

  // Active quiz
  const question = quiz.questions[currentQuestion];

  return (
    <div className="max-w-3xl mx-auto">
      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-dark-400 mb-2">
          <span>Question {currentQuestion + 1} of {quiz.questions.length}</span>
          <span className="flex items-center gap-1">
            <FiClock className="w-4 h-4" />
            {quiz.difficulty}
          </span>
        </div>
        <div className="w-full bg-dark-800 rounded-full h-2">
          <motion.div
            className="bg-primary-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${((currentQuestion + 1) / quiz.questions.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <motion.div
        key={currentQuestion}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="card"
      >
        <div className="flex items-center gap-2 mb-4">
          <span className="px-2 py-1 bg-dark-700 text-dark-300 text-xs rounded capitalize">
            {question.question_type.replace('_', ' ')}
          </span>
          <span className="text-dark-500 text-xs">{question.points} pts</span>
        </div>

        <h2 className="text-lg font-medium text-dark-100 mb-6">{question.question_text}</h2>

        {/* MCQ Options */}
        {question.question_type === 'mcq' && question.options ? (
          <div className="space-y-3">
            {question.options.map((option, i) => (
              <button
                key={i}
                onClick={() => setAnswers({ ...answers, [question.id]: option })}
                className={`w-full text-left p-4 rounded-lg border transition-all ${
                  answers[question.id] === option
                    ? 'border-primary-500 bg-primary-600/10 text-primary-300'
                    : 'border-dark-700 bg-dark-900 text-dark-300 hover:border-dark-500'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
        ) : (
          /* Text input for short answer / conceptual */
          <textarea
            className="input-field w-full h-32 resize-none"
            placeholder="Type your answer..."
            value={answers[question.id] || ''}
            onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
          />
        )}
      </motion.div>

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <button
          onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
          disabled={currentQuestion === 0}
          className="btn-secondary disabled:opacity-50"
        >
          Previous
        </button>

        {currentQuestion < quiz.questions.length - 1 ? (
          <button
            onClick={() => setCurrentQuestion(currentQuestion + 1)}
            className="btn-primary"
          >
            Next Question
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="btn-primary flex items-center gap-2"
          >
            <FiAward className="w-4 h-4" />
            {loading ? 'Submitting...' : 'Submit Quiz'}
          </button>
        )}
      </div>
    </div>
  );
}
