'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import {
  ArrowLeft, Sparkles, RotateCcw, ThumbsUp, ThumbsDown,
  Loader2, Eye, EyeOff
} from 'lucide-react';
import toast from 'react-hot-toast';
import { revisionAPI, courseAPI } from '@/services/api';
import { Flashcard } from '@/types';

export default function FlashcardsPage() {
  const params = useParams();
  const courseId = Number(params.id);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [topic, setTopic] = useState('');
  const [generating, setGenerating] = useState(false);
  const queryClient = useQueryClient();

  const { data: course } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => courseAPI.getById(courseId),
  });

  const { data: flashcards = [], refetch } = useQuery({
    queryKey: ['flashcards', courseId],
    queryFn: () => revisionAPI.getFlashcards(courseId),
  });

  const generateFlashcards = async () => {
    setGenerating(true);
    try {
      await revisionAPI.generateFlashcards({
        course_id: courseId,
        topic: topic || undefined,
        num_cards: 10,
      });
      refetch();
      toast.success('Flashcards generated!');
    } catch (err) {
      toast.error('Failed to generate flashcards');
    } finally {
      setGenerating(false);
    }
  };

  const reviewCard = async (quality: number) => {
    if (!flashcards[currentIndex]) return;
    try {
      await revisionAPI.reviewFlashcard({
        flashcard_id: flashcards[currentIndex].id,
        quality,
      });
      setShowAnswer(false);
      if (currentIndex < flashcards.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        toast.success('Review complete!');
        setCurrentIndex(0);
        refetch();
      }
    } catch (err) {
      toast.error('Failed to save review');
    }
  };

  const currentCard = flashcards[currentIndex];

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 glass border-b border-border">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href={`/course/${courseId}`} className="p-2 rounded-xl hover:bg-secondary">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="font-bold">Flashcards</h1>
              <p className="text-xs text-muted-foreground">{course?.title}</p>
            </div>
          </div>
          {flashcards.length > 0 && (
            <span className="text-sm text-muted-foreground">
              {currentIndex + 1} / {flashcards.length}
            </span>
          )}
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-2xl">
        {/* Generator */}
        <div className="p-6 rounded-2xl bg-card border border-border mb-8">
          <h2 className="font-semibold mb-3 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            Generate Flashcards
          </h2>
          <div className="flex gap-3">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Topic (optional)"
              className="flex-1 px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
            <button
              onClick={generateFlashcards}
              disabled={generating}
              className="px-5 py-2.5 rounded-xl bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
            >
              {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Generate
            </button>
          </div>
        </div>

        {/* Flashcard Display */}
        {flashcards.length > 0 && currentCard ? (
          <div className="space-y-6">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentCard.id}
                initial={{ opacity: 0, rotateY: -90 }}
                animate={{ opacity: 1, rotateY: 0 }}
                exit={{ opacity: 0, rotateY: 90 }}
                transition={{ duration: 0.3 }}
                className="min-h-[300px] p-8 rounded-2xl bg-card border border-border flex flex-col items-center justify-center text-center cursor-pointer"
                onClick={() => setShowAnswer(!showAnswer)}
              >
                {!showAnswer ? (
                  <>
                    <p className="text-xs text-muted-foreground mb-4 flex items-center gap-1">
                      <Eye className="w-3 h-3" /> Click to reveal answer
                    </p>
                    <p className="text-lg font-medium">{currentCard.question}</p>
                    {currentCard.topic && (
                      <span className="mt-4 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs">
                        {currentCard.topic}
                      </span>
                    )}
                  </>
                ) : (
                  <>
                    <p className="text-xs text-muted-foreground mb-4 flex items-center gap-1">
                      <EyeOff className="w-3 h-3" /> Answer
                    </p>
                    <p className="text-lg">{currentCard.answer}</p>
                  </>
                )}
              </motion.div>
            </AnimatePresence>

            {/* Review Buttons */}
            {showAnswer && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-center gap-4"
              >
                <button
                  onClick={() => reviewCard(1)}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl border border-red-500/30 text-red-500 hover:bg-red-500/10 transition-colors"
                >
                  <ThumbsDown className="w-4 h-4" /> Hard
                </button>
                <button
                  onClick={() => reviewCard(3)}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl border border-yellow-500/30 text-yellow-500 hover:bg-yellow-500/10 transition-colors"
                >
                  <RotateCcw className="w-4 h-4" /> Okay
                </button>
                <button
                  onClick={() => reviewCard(5)}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl border border-green-500/30 text-green-500 hover:bg-green-500/10 transition-colors"
                >
                  <ThumbsUp className="w-4 h-4" /> Easy
                </button>
              </motion.div>
            )}

            {/* Progress bar */}
            <div className="w-full h-2 rounded-full bg-secondary overflow-hidden">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${((currentIndex + 1) / flashcards.length) * 100}%` }}
              />
            </div>
          </div>
        ) : (
          !generating && (
            <div className="text-center py-16 text-muted-foreground">
              <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>No flashcards yet. Generate some above!</p>
            </div>
          )
        )}
      </main>
    </div>
  );
}
