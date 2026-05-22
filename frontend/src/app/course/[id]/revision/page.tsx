'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import {
  ArrowLeft, FileText, Sparkles, BookOpen, Calculator,
  Loader2, Clock
} from 'lucide-react';
import toast from 'react-hot-toast';
import { revisionAPI, courseAPI } from '@/services/api';
import { RevisionContent } from '@/types';

const revisionTypes = [
  { id: 'cheat_sheet', label: 'Cheat Sheet', icon: FileText, desc: 'Key points & formulas' },
  { id: 'formula_sheet', label: 'Formula Sheet', icon: Calculator, desc: 'All formulas organized' },
  { id: 'quick_notes', label: 'Quick Notes', icon: BookOpen, desc: 'Brief revision notes' },
  { id: 'exam_summary', label: 'Exam Summary', icon: Sparkles, desc: 'Night-before-exam summary' },
];

export default function RevisionPage() {
  const params = useParams();
  const courseId = Number(params.id);
  const [selectedType, setSelectedType] = useState('cheat_sheet');
  const [topic, setTopic] = useState('');
  const [generatedContent, setGeneratedContent] = useState<RevisionContent | null>(null);
  const [generating, setGenerating] = useState(false);

  const { data: course } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => courseAPI.getById(courseId),
  });

  const { data: revisions = [] } = useQuery({
    queryKey: ['revisions', courseId],
    queryFn: () => revisionAPI.getAll(courseId),
  });

  const generateRevision = async () => {
    setGenerating(true);
    try {
      const result = await revisionAPI.generate({
        course_id: courseId,
        revision_type: selectedType,
        topic: topic || undefined,
      });
      setGeneratedContent(result);
      toast.success('Revision material generated!');
    } catch (err) {
      toast.error('Failed to generate. Check your API key.');
    } finally {
      setGenerating(false);
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
            <h1 className="font-bold">Revision</h1>
            <p className="text-xs text-muted-foreground">{course?.title}</p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Generator */}
        <div className="p-6 rounded-2xl bg-card border border-border mb-8">
          <h2 className="font-semibold text-lg mb-4">Generate Revision Material</h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            {revisionTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => setSelectedType(type.id)}
                className={`p-3 rounded-xl border text-center transition-all text-sm
                  ${selectedType === type.id ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/30'}`}
              >
                <type.icon className={`w-5 h-5 mx-auto mb-1 ${selectedType === type.id ? 'text-primary' : 'text-muted-foreground'}`} />
                <p className="font-medium text-xs">{type.label}</p>
              </button>
            ))}
          </div>

          <div className="flex gap-3">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Topic (optional - leave empty for full course)"
              className="flex-1 px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
            <button
              onClick={generateRevision}
              disabled={generating}
              className="px-6 py-2.5 rounded-xl bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
            >
              {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Generate
            </button>
          </div>
        </div>

        {/* Generated Content */}
        {generatedContent && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-card border border-border mb-8"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">{generatedContent.topic} - {generatedContent.revision_type.replace('_', ' ')}</h3>
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {new Date(generatedContent.created_at).toLocaleDateString()}
              </span>
            </div>
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                {generatedContent.content}
              </ReactMarkdown>
            </div>
          </motion.div>
        )}

        {/* Previous Revisions */}
        {revisions.length > 0 && (
          <div>
            <h2 className="font-semibold text-lg mb-4">Previous Revisions</h2>
            <div className="space-y-3">
              {revisions.map((rev: RevisionContent) => (
                <div
                  key={rev.id}
                  className="p-4 rounded-xl bg-card border border-border cursor-pointer hover:border-primary/30 transition-colors"
                  onClick={() => setGeneratedContent(rev)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">{rev.topic}</p>
                      <p className="text-xs text-muted-foreground capitalize">{rev.revision_type.replace('_', ' ')}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(rev.created_at).toLocaleDateString()}
                    </span>
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
