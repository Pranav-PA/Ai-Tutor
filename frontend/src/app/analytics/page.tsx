'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { adaptiveAPI } from '@/lib/api';
import { useCourseStore } from '@/store';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { FiTrendingUp, FiTarget, FiClock, FiAward } from 'react-icons/fi';

export default function AnalyticsPage() {
  const { currentCourse } = useCourseStore();
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!currentCourse?.id) {
        setLoading(false);
        return;
      }
      try {
        const res = await adaptiveAPI.getAnalytics(currentCourse.id);
        setAnalytics(res.data);
      } catch (error) {
        console.error('Failed to fetch analytics');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [currentCourse]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!analytics || !currentCourse) {
    return (
      <div className="text-center py-20">
        <span className="text-6xl block mb-4">📊</span>
        <h2 className="text-2xl font-bold text-dark-100 mb-2">No Analytics Yet</h2>
        <p className="text-dark-400">Start learning to see your performance analytics.</p>
      </div>
    );
  }

  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b'];

  const completionData = [
    { name: 'Completed', value: analytics.completed_topics },
    { name: 'Remaining', value: analytics.total_topics - analytics.completed_topics },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-dark-50">Analytics</h1>
        <p className="text-dark-400 mt-1">{currentCourse.title} - Performance Overview</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { icon: FiTarget, label: 'Completion', value: `${analytics.completion_percentage}%`, color: 'primary' },
          { icon: FiAward, label: 'Avg Score', value: `${analytics.average_score}%`, color: 'green' },
          { icon: FiClock, label: 'Time Spent', value: `${Math.round(analytics.total_time_spent_minutes / 60)}h`, color: 'blue' },
          { icon: FiTrendingUp, label: 'Topics Done', value: `${analytics.completed_topics}/${analytics.total_topics}`, color: 'purple' },
        ].map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-dark-700 flex items-center justify-center">
                <stat.icon className="w-5 h-5 text-primary-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-dark-50">{stat.value}</p>
                <p className="text-xs text-dark-400">{stat.label}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Score History */}
        <div className="card">
          <h3 className="text-lg font-semibold text-dark-100 mb-4">Score History</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={analytics.score_history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#6366f1"
                strokeWidth={2}
                dot={{ fill: '#6366f1' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Completion Pie */}
        <div className="card">
          <h3 className="text-lg font-semibold text-dark-100 mb-4">Progress</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={completionData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                label
              >
                {completionData.map((_, index) => (
                  <Cell key={index} fill={index === 0 ? '#6366f1' : '#334155'} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Topic Performance */}
      <div className="card">
        <h3 className="text-lg font-semibold text-dark-100 mb-4">Topic Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={analytics.topic_performance}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="topic" stroke="#64748b" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={80} />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
            />
            <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Weak & Strong Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-red-400 mb-4">⚠️ Weak Areas</h3>
          {analytics.weak_areas.length === 0 ? (
            <p className="text-dark-500">No weak areas identified yet.</p>
          ) : (
            <div className="space-y-2">
              {analytics.weak_areas.map((area: string, i: number) => (
                <div key={i} className="p-3 bg-red-600/10 border border-red-600/20 rounded-lg">
                  <p className="text-dark-300 text-sm">{area}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-green-400 mb-4">✅ Strong Areas</h3>
          {analytics.strong_areas.length === 0 ? (
            <p className="text-dark-500">Complete more topics to see strong areas.</p>
          ) : (
            <div className="space-y-2">
              {analytics.strong_areas.map((area: string, i: number) => (
                <div key={i} className="p-3 bg-green-600/10 border border-green-600/20 rounded-lg">
                  <p className="text-dark-300 text-sm">{area}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
