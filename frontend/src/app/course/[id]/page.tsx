'use client';

import { useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  BookOpen, MessageCircle, Brain, FileText, BarChart3,
  Clock, Sparkles, Upload, ArrowLeft, Layers, Calendar,
  ChevronRight, Zap
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { courseAPI, documentAPI } from '@/services/api';
import { Course, Document } from '@/types';

const navItems = [
  { icon: BookOpen, label: 'Learn', href: 'learn', desc: 'AI-powered lessons' },
  { icon: MessageCircle, label: 'AI Chat', href: 'chat', desc: 'Ask anything' },
  { icon: Brain, label: 'Quiz', href: 'quiz', desc: 'Test yourself' },
  { icon: Layers, label: 'Revision', href: 'revision', desc: 'Cheat sheets & notes' },
  { icon: Sparkles, label: 'Flashcards', href: 'flashcards', desc: 'Spaced repetition' },
  { icon: BarChart3, label: 'Analytics', href: 'analytics', desc: 'Track progress' },
];

export default function CoursePage() {
  const params = useParams();
  const router = useRouter();
  const courseId = Number(params.id);
  const [uploading, setUploading] = useState(false);
  const [selectedDocumentTag, setSelectedDocumentTag] = useState('notes');

  const documentTagOptions = [
    { value: 'syllabus', label: 'Syllabus' },
    { value: 'notes', label: 'Notes' },
    { value: 'previous_year_question_paper', label: 'Previous Year Question Paper' },
    { value: 'assignment', label: 'Assignment' },
    { value: 'reference_book', label: 'Reference Book' },
    { value: 'lab_manual', label: 'Lab Manual' },
    { value: 'other', label: 'Other' },
  ];

  const formatDocumentTag = (tag?: string) => {
    if (!tag) return 'Uncategorized';
    const matched = documentTagOptions.find((option) => option.value === tag);
    if (matched) return matched.label;
    return tag.replaceAll('_', ' ');
  };

  const { data: course, isLoading: courseLoading } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => courseAPI.getById(courseId),
  });

  const { data: documents = [], refetch: refetchDocs } = useQuery({
    queryKey: ['documents', courseId],
    queryFn: () => documentAPI.getAll(courseId),
  });

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    try {
      for (const file of acceptedFiles) {
        await documentAPI.upload(courseId, file, selectedDocumentTag);
        toast.success(`Uploaded: ${file.name} (${formatDocumentTag(selectedDocumentTag)})`);
      }
      refetchDocs();
    } catch (err) {
      toast.error('Upload failed');
    } finally {
      setUploading(false);
    }
  }, [courseId, refetchDocs, selectedDocumentTag]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/plain': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
    maxSize: 50 * 1024 * 1024,
  });

  if (courseLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-primary/20" />
          <div className="w-32 h-4 rounded bg-muted" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-border">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <button onClick={() => router.push('/dashboard')} className="p-2 rounded-xl hover:bg-secondary transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3 flex-1">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: `${course?.color || '#6366f1'}20` }}
            >
              <BookOpen className="w-5 h-5" style={{ color: course?.color || '#6366f1' }} />
            </div>
            <div>
              <h1 className="font-bold text-lg">{course?.title}</h1>
              <p className="text-xs text-muted-foreground">
                {course?.subject} {course?.semester && `• ${course.semester}`}
              </p>
            </div>
          </div>
          {course?.exam_date && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-orange-500/10 text-orange-500 text-sm">
              <Calendar className="w-4 h-4" />
              <span>{new Date(course.exam_date).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-5xl">
        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="p-4 rounded-2xl bg-card border border-border text-center">
            <p className="text-2xl font-bold text-primary">{documents.length}</p>
            <p className="text-xs text-muted-foreground">Documents</p>
          </div>
          <div className="p-4 rounded-2xl bg-card border border-border text-center">
            <p className="text-2xl font-bold text-green-500">{Math.round(course?.progress_percentage || 0)}%</p>
            <p className="text-xs text-muted-foreground">Progress</p>
          </div>
          <div className="p-4 rounded-2xl bg-card border border-border text-center">
            <p className="text-2xl font-bold text-purple-500">{course?.quiz_count || 0}</p>
            <p className="text-xs text-muted-foreground">Quizzes</p>
          </div>
        </div>

        {/* Navigation Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {navItems.map((item, i) => (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link href={`/course/${courseId}/${item.href}`}>
                <div className="p-5 rounded-2xl bg-card border border-border hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all group cursor-pointer">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                        <item.icon className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{item.label}</h3>
                        <p className="text-xs text-muted-foreground">{item.desc}</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5 text-primary" />
            Upload Materials
          </h2>
          <div className="mb-4 rounded-xl bg-card border border-border p-4">
            <label htmlFor="document-tag" className="block text-sm font-medium mb-2">
              Tag this upload as
            </label>
            <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
              <select
                id="document-tag"
                value={selectedDocumentTag}
                onChange={(e) => setSelectedDocumentTag(e.target.value)}
                className="w-full sm:w-auto min-w-[280px] px-3 py-2 rounded-lg bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                disabled={uploading}
              >
                {documentTagOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-muted-foreground">
                Example: choose <span className="font-medium">Syllabus</span> for outline PDFs, then switch to
                <span className="font-medium"> Notes</span> or <span className="font-medium">Previous Year Question Paper</span> for your next uploads.
              </p>
            </div>
          </div>
          <div
            {...getRootProps()}
            className={`p-8 rounded-2xl border-2 border-dashed transition-all cursor-pointer text-center
              ${isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
              ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
          >
            <input {...getInputProps()} />
            <Upload className="w-8 h-8 mx-auto mb-3 text-muted-foreground" />
            {isDragActive ? (
              <p className="text-primary font-medium">Drop files here...</p>
            ) : (
              <>
                <p className="font-medium mb-1">Drag & drop files here, or click to browse</p>
                <p className="text-sm text-muted-foreground">Selected tag: <span className="font-medium">{formatDocumentTag(selectedDocumentTag)}</span></p>
                <p className="text-sm text-muted-foreground">PDF, DOCX, PPTX, TXT, PNG, JPG (max 50MB)</p>
              </>
            )}
            {uploading && <p className="text-primary mt-2 text-sm">Processing...</p>}
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            You can upload more documents anytime. Change the tag and upload again for notes, PYQs, assignments, and more.
          </p>
        </div>

        {/* Documents List */}
        {documents.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              Uploaded Documents
            </h2>
            <div className="space-y-2">
              {documents.map((doc: Document) => (
                <div
                  key={doc.id}
                  className="p-4 rounded-xl bg-card border border-border flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium text-sm">{doc.filename}</p>
                      <p className="text-xs text-muted-foreground">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-primary/10 text-primary mr-1">
                          {formatDocumentTag(doc.document_tag)}
                        </span>
                        {(doc.file_size / 1024).toFixed(1)} KB • {doc.chunk_count} chunks
                        {!doc.is_processed && ' • Processing...'}
                      </p>
                    </div>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${doc.is_processed ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'}`} />
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
