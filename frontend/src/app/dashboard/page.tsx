'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { ingestionAPI, learningAPI } from '@/lib/api';
import { useCourseStore, useAuthStore } from '@/store';
import Link from 'next/link';
import { FiPlus, FiUpload, FiPlay, FiCheckCircle, FiClock, FiTarget } from 'react-icons/fi';

export default function DashboardPage() {
  const { courses, setCourses, setCurrentCourse } = useCourseStore();
  const { user } = useAuthStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [newCourseTitle, setNewCourseTitle] = useState('');
  const [progress, setProgress] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchCourses = useCallback(async () => {
    try {
      const res = await ingestionAPI.listCourses();
      setCourses(res.data);
    } catch (error) {
      console.error('Failed to fetch courses');
    } finally {
      setLoading(false);
    }
  }, [setCourses]);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  const handleCreateCourse = async () => {
    if (!newCourseTitle.trim()) return;
    try {
      const res = await ingestionAPI.createCourse({ title: newCourseTitle });
      setCourses([...courses, res.data]);
      setNewCourseTitle('');
      setShowCreateModal(false);
      toast.success('Course created!');
    } catch (error) {
      toast.error('Failed to create course');
    }
  };

  const handleUpload = async (files: FileList, docType: string) => {
    if (!selectedCourse || !files.length) return;
    try {
      await ingestionAPI.uploadDocuments(selectedCourse, Array.from(files), docType);
      toast.success(`${files.length} file(s) uploaded!`);
    } catch (error) {
      toast.error('Upload failed');
    }
  };

  const handleProcessCourse = async (courseId: string) => {
    try {
      toast.loading('Processing course...', { id: 'process' });
      await ingestionAPI.processCourse(courseId);
      toast.success('Course processed! Roadmap generated.', { id: 'process' });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Processing failed', { id: 'process' });
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-dark-50">
            Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}! 👋
          </h1>
          <p className="text-dark-400 mt-1">Continue your learning journey</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <FiPlus className="w-4 h-4" />
          New Course
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { icon: FiTarget, label: 'Courses', value: courses.length, color: 'primary' },
          { icon: FiCheckCircle, label: 'Completed', value: '0', color: 'green' },
          { icon: FiClock, label: 'Hours Studied', value: '0', color: 'blue' },
          { icon: FiPlay, label: 'In Progress', value: '0', color: 'yellow' },
        ].map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card flex items-center gap-4"
          >
            <div className={`w-12 h-12 rounded-lg bg-${stat.color}-600/20 flex items-center justify-center`}>
              <stat.icon className={`w-6 h-6 text-${stat.color}-400`} />
            </div>
            <div>
              <p className="text-2xl font-bold text-dark-50">{stat.value}</p>
              <p className="text-sm text-dark-400">{stat.label}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Courses Grid */}
      <div>
        <h2 className="text-xl font-semibold text-dark-100 mb-4">Your Courses</h2>
        {loading ? (
          <div className="text-center py-12 text-dark-400">Loading...</div>
        ) : courses.length === 0 ? (
          <div className="card text-center py-12">
            <span className="text-4xl mb-4 block">📚</span>
            <h3 className="text-lg font-medium text-dark-200 mb-2">No courses yet</h3>
            <p className="text-dark-400 mb-4">Create your first course to get started</p>
            <button onClick={() => setShowCreateModal(true)} className="btn-primary">
              Create Course
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {courses.map((course, i) => (
              <motion.div
                key={course.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="card hover:border-primary-500/50 transition-all cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-dark-100 group-hover:text-primary-400 transition-colors">
                    {course.title}
                  </h3>
                </div>
                {course.description && (
                  <p className="text-sm text-dark-400 mb-4">{course.description}</p>
                )}
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => { setSelectedCourse(course.id); setShowUploadModal(true); }}
                    className="btn-secondary text-xs flex items-center gap-1"
                  >
                    <FiUpload className="w-3 h-3" /> Upload
                  </button>
                  <button
                    onClick={() => handleProcessCourse(course.id)}
                    className="btn-secondary text-xs flex items-center gap-1"
                  >
                    <FiPlay className="w-3 h-3" /> Process
                  </button>
                  <Link
                    href={`/learning?course=${course.id}`}
                    onClick={() => setCurrentCourse(course)}
                    className="btn-primary text-xs flex items-center gap-1"
                  >
                    Learn →
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Create Course Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card w-full max-w-md"
          >
            <h2 className="text-xl font-bold text-dark-50 mb-4">Create New Course</h2>
            <input
              type="text"
              className="input-field w-full mb-4"
              placeholder="Course Title (e.g., Data Structures)"
              value={newCourseTitle}
              onChange={(e) => setNewCourseTitle(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreateCourse()}
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowCreateModal(false)} className="btn-secondary">Cancel</button>
              <button onClick={handleCreateCourse} className="btn-primary">Create</button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card w-full max-w-lg"
          >
            <h2 className="text-xl font-bold text-dark-50 mb-4">Upload Documents</h2>
            <p className="text-dark-400 text-sm mb-6">
              Upload your syllabus, notes, and previous year papers.
            </p>

            <div className="space-y-4">
              {['syllabus', 'notes', 'pyq'].map((type) => (
                <div key={type} className="flex items-center gap-4 p-4 bg-dark-900 rounded-lg">
                  <span className="text-2xl">
                    {type === 'syllabus' ? '📄' : type === 'notes' ? '📘' : '📝'}
                  </span>
                  <div className="flex-1">
                    <p className="text-dark-200 font-medium capitalize">{type}</p>
                    <p className="text-dark-500 text-xs">PDF, DOCX, or images</p>
                  </div>
                  <label className="btn-secondary text-xs cursor-pointer">
                    Choose Files
                    <input
                      type="file"
                      multiple
                      className="hidden"
                      accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
                      onChange={(e) => e.target.files && handleUpload(e.target.files, type)}
                    />
                  </label>
                </div>
              ))}
            </div>

            <div className="flex justify-end mt-6">
              <button onClick={() => setShowUploadModal(false)} className="btn-secondary">Close</button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
