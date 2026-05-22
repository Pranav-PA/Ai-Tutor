'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { ArrowLeft, BookOpen, Loader2, Play } from 'lucide-react';
import toast from 'react-hot-toast';
import { courseAPI, chatAPI } from '@/services/api';

export default function LearnPage() {
  const params = useParams();
  const courseId = Number(params.id);
  const [topic, setTopic] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const { data: course } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => courseAPI.getById(courseId),
  });

  const startLesson = async () => {
    if (!topic.trim()) return toast.error('Enter a topic to learn');
    setLoading(true);
    setContent('');

    try {
      let fullContent = '';
      for await (const chunk of chatAPI.stream({
        content: `Teach me about: ${topic}. Follow this structure:
1. Brief Overview
2. Key Concepts (explained step by step)
3. Examples
4. Common Mistakes to Avoid
5. Quick Summary
6. A practice question to test understanding`,
        mode: 'explain',
        course_id: courseId,
      })) {
        fullContent += chunk;
        setContent(fullContent);
      }
    } catch (err) {
      toast.error('Failed to generate lesson');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 glass border-b border-border">
        <div className="container mx-auto px-6 py-4 flex items-center gap-3">
          <Link href={`/course/${courseId}`} className="p-2 rounded-xl hover:bg-secondary">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="font-bold">Learn</h1>
            <p className="text-xs text-muted-foreground">{course?.title}</p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-3xl">
        {/* Topic Input */}
        <div className="p-6 rounded-2xl bg-card border border-border mb-8">
          <h2 className="font-semibold mb-3 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary" />
            What would you like to learn?
          </h2>
          <div className="flex gap-3">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && startLesson()}
              placeholder="e.g., Binary Search Trees, Neural Networks, Integration..."
              className="flex-1 px-4 py-3 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
            <button
              onClick={startLesson}
              disabled={loading}
              className="px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Learn
            </button>
          </div>
        </div>

        {/* Lesson Content */}
        {content && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-card border border-border"
          >
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                {content}
              </ReactMarkdown>
            </div>
          </motion.div>
        )}

        {!content && !loading && (
          <div className="text-center py-16 text-muted-foreground">
            <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-30" />
            <p className="mb-2">Enter a topic above to start learning</p>
            <p className="text-sm">AI will teach you step-by-step using your uploaded materials</p>
          </div>
        )}
      </main>
    </div>
  );
}
