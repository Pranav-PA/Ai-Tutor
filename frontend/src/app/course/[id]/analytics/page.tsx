'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  ArrowLeft, BarChart3, TrendingUp, Target, Brain,
  Clock, Flame, AlertTriangle, CheckCircle2
} from 'lucide-react';
import { analyticsAPI, courseAPI } from '@/services/api';
import { Analytics } from '@/types';

export default function AnalyticsPage() {
  const params = useParams();
  const courseId = Number(params.id);

  const { data: course } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => courseAPI.getById(courseId),
  });

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', courseId],
    queryFn: () => analyticsAPI.get(courseId),
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading analytics...</div>
      </div>
    );
  }

  const data: Analytics = analytics || {
    syllabus_completion: 0,
    quiz_accuracy: 0,
    weak_topics: [],
    strong_topics: [],
    total_study_hours: 0,
    revision_streak: 0,
    ai_readiness_score: 0,
    topics_by_confidence: [],
    quiz_history: [],
    study_sessions: [],
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 glass border-b border-border">
        <div className="container mx-auto px-6 py-4 flex items-center gap-3">
          <Link href={`/course/${courseId}`} className="p-2 rounded-xl hover:bg-secondary">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="font-bold">Analytics</h1>
            <p className="text-xs text-muted-foreground">{course?.title}</p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-5xl">
        {/* Readiness Score */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-8 rounded-2xl bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-pink-500/10 border border-primary/20 text-center mb-8"
        >
          <h2 className="text-sm text-muted-foreground mb-2">AI Exam Readiness Score</h2>
          <div className="relative w-32 h-32 mx-auto mb-4">
            <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="52" fill="none" stroke="hsl(var(--border))" strokeWidth="8" />
              <circle
                cx="60" cy="60" r="52" fill="none"
                stroke="url(#gradient)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${(data.ai_readiness_score / 100) * 327} 327`}
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-3xl font-bold">{Math.round(data.ai_readiness_score)}</span>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            {data.ai_readiness_score >= 80 ? "You're well prepared!" :
             data.ai_readiness_score >= 50 ? "Keep going, you're making progress!" :
             "Focus on weak areas to improve your readiness."}
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon: Target, label: 'Syllabus', value: `${data.syllabus_completion}%`, color: 'text-indigo-500' },
            { icon: TrendingUp, label: 'Quiz Accuracy', value: `${data.quiz_accuracy}%`, color: 'text-green-500' },
            { icon: Clock, label: 'Study Hours', value: `${data.total_study_hours}h`, color: 'text-blue-500' },
            { icon: Flame, label: 'Streak', value: `${data.revision_streak} days`, color: 'text-orange-500' },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="p-4 rounded-2xl bg-card border border-border"
            >
              <stat.icon className={`w-5 h-5 mb-2 ${stat.color}`} />
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-xs text-muted-foreground">{stat.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Topics Confidence */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Weak Topics */}
          <div className="p-6 rounded-2xl bg-card border border-border">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              Weak Topics ({data.weak_topics.length})
            </h3>
            {data.weak_topics.length > 0 ? (
              <div className="space-y-2">
                {data.weak_topics.map((topic) => (
                  <div key={topic} className="px-3 py-2 rounded-lg bg-orange-500/10 text-orange-500 text-sm">
                    {topic}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No weak topics identified yet. Take some quizzes!</p>
            )}
          </div>

          {/* Strong Topics */}
          <div className="p-6 rounded-2xl bg-card border border-border">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              Strong Topics ({data.strong_topics.length})
            </h3>
            {data.strong_topics.length > 0 ? (
              <div className="space-y-2">
                {data.strong_topics.map((topic) => (
                  <div key={topic} className="px-3 py-2 rounded-lg bg-green-500/10 text-green-500 text-sm">
                    {topic}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Keep studying to build strength in topics!</p>
            )}
          </div>
        </div>

        {/* Topic Confidence Bars */}
        {data.topics_by_confidence.length > 0 && (
          <div className="p-6 rounded-2xl bg-card border border-border">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Brain className="w-4 h-4 text-primary" />
              Topic Confidence
            </h3>
            <div className="space-y-3">
              {data.topics_by_confidence.map((topic) => (
                <div key={topic.topic} className="flex items-center gap-3">
                  <span className="text-sm w-40 truncate">{topic.topic}</span>
                  <div className="flex-1 h-2 rounded-full bg-secondary overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        topic.confidence >= 0.7 ? 'bg-green-500' :
                        topic.confidence >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${topic.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground w-12 text-right">
                    {Math.round(topic.confidence * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
