'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import {
  Plus, BookOpen, Clock, BarChart3, Brain, Search,
  Trash2, Archive, MoreVertical, Calendar, GraduationCap,
  Settings, Moon, Sun
} from 'lucide-react';
import { useTheme } from 'next-themes';
import toast from 'react-hot-toast';
import { courseAPI } from '@/services/api';
import { Course } from '@/types';
import { useAppStore } from '@/store';

export default function DashboardPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { theme, setTheme } = useTheme();
  const { setCourses } = useAppStore();
  const queryClient = useQueryClient();

  const { data: courses = [], isLoading } = useQuery({
    queryKey: ['courses'],
    queryFn: courseAPI.getAll,
  });

  useEffect(() => {
    if (courses.length > 0) setCourses(courses);
  }, [courses, setCourses]);

  const deleteMutation = useMutation({
    mutationFn: courseAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      toast.success('Course deleted');
    },
  });

  const filteredCourses = courses.filter((c: Course) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-strong border-b border-border shadow-sm">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/25">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <h1 className="font-display font-bold text-xl">My Courses</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search courses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-4 py-2 rounded-xl bg-secondary border border-border text-sm w-64 focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded-xl hover:bg-secondary transition-colors"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <Link href="/settings" className="p-2 rounded-xl hover:bg-secondary transition-colors">
              <Settings className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon: BookOpen, label: 'Total Courses', value: courses.length, color: 'text-indigo-500' },
            { icon: GraduationCap, label: 'Active', value: courses.filter((c: Course) => !c.is_archived).length, color: 'text-green-500' },
            { icon: BarChart3, label: 'Avg Progress', value: `${Math.round(courses.reduce((a: number, c: Course) => a + c.progress_percentage, 0) / Math.max(courses.length, 1))}%`, color: 'text-purple-500' },
            { icon: Calendar, label: 'Upcoming Exams', value: courses.filter((c: Course) => c.exam_date).length, color: 'text-orange-500' },
          ].map((stat) => (
            <motion.div
              key={stat.label}
              className="p-4 rounded-2xl bg-card border border-border"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-xl bg-secondary ${stat.color}`}>
                  <stat.icon className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs text-muted-foreground">{stat.label}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Course Grid */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold">Your Courses</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" /> New Course
          </button>
        </div>

        {isLoading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 rounded-2xl bg-card border border-border animate-pulse" />
            ))}
          </div>
        ) : filteredCourses.length === 0 ? (
          <motion.div
            className="text-center py-20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-8 h-8 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">No courses yet</h3>
            <p className="text-muted-foreground mb-6">Create your first course to get started with AI tutoring</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium"
            >
              <Plus className="w-4 h-4" /> Create Course
            </button>
          </motion.div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence>
              {filteredCourses.map((course: Course, i: number) => (
                <motion.div
                  key={course.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link href={`/course/${course.id}`}>
                    <div className="p-6 rounded-2xl bg-card border border-border hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all group cursor-pointer">
                      <div className="flex items-start justify-between mb-4">
                        <div
                          className="w-10 h-10 rounded-xl flex items-center justify-center"
                          style={{ backgroundColor: `${course.color}20` }}
                        >
                          <BookOpen className="w-5 h-5" style={{ color: course.color }} />
                        </div>
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            if (confirm('Delete this course?')) deleteMutation.mutate(course.id);
                          }}
                          className="p-1.5 rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors opacity-0 group-hover:opacity-100"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <h3 className="font-semibold text-lg mb-1 group-hover:text-primary transition-colors">
                        {course.title}
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        {course.subject || course.semester || 'No description'}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                          <span>{course.document_count} docs</span>
                          <span>{course.quiz_count} quizzes</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-16 h-1.5 rounded-full bg-secondary overflow-hidden">
                            <div
                              className="h-full rounded-full bg-primary transition-all"
                              style={{ width: `${course.progress_percentage}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground">{Math.round(course.progress_percentage)}%</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </main>

      {/* Create Course Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <CreateCourseModal onClose={() => setShowCreateModal(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}

function CreateCourseModal({ onClose }: { onClose: () => void }) {
  const [formData, setFormData] = useState({
    title: '',
    semester: '',
    university: '',
    subject: '',
    exam_date: '',
    color: '#6366f1',
  });
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: courseAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      toast.success('Course created!');
      onClose();
    },
    onError: (err: any) => toast.error(err.message || 'Failed to create course'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return toast.error('Course title is required');
    createMutation.mutate({
      ...formData,
      exam_date: formData.exam_date ? new Date(formData.exam_date).toISOString() : null,
    });
  };

  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#06b6d4'];

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <motion.div
        className="relative w-full max-w-md rounded-2xl bg-card border border-border p-6 shadow-2xl"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
      >
        <h2 className="text-xl font-bold mb-6">Create New Course</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">Course Title *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Machine Learning"
              className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              autoFocus
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Semester</label>
              <input
                type="text"
                value={formData.semester}
                onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                placeholder="e.g., Fall 2024"
                className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Subject</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="e.g., CS"
                className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">University</label>
            <input
              type="text"
              value={formData.university}
              onChange={(e) => setFormData({ ...formData, university: e.target.value })}
              placeholder="e.g., MIT"
              className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Exam Date</label>
            <input
              type="date"
              value={formData.exam_date}
              onChange={(e) => setFormData({ ...formData, exam_date: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Color</label>
            <div className="flex gap-2">
              {colors.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setFormData({ ...formData, color })}
                  className={`w-8 h-8 rounded-full transition-transform ${formData.color === color ? 'scale-125 ring-2 ring-offset-2 ring-offset-card ring-primary' : ''}`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 rounded-xl border border-border font-medium text-sm hover:bg-secondary transition-colors">
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 px-4 py-2.5 rounded-xl bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Course'}
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
}
