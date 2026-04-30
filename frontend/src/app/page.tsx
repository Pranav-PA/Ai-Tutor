'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { useAuthStore } from '@/store';

export default function HomePage() {
  const { isAuthenticated } = useAuthStore();

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-dark-950 via-dark-900 to-primary-950 -z-10" />
      
      {/* Animated glow */}
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary-600/10 rounded-full blur-3xl -z-10" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center max-w-4xl"
      >
        {/* Logo */}
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8"
        >
          <span className="text-6xl">🎓</span>
        </motion.div>

        {/* Title */}
        <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-primary-400 to-primary-200 bg-clip-text text-transparent mb-6">
          AI Learning Engine
        </h1>

        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-dark-300 mb-12 max-w-2xl mx-auto">
          Intelligent, adaptive learning powered by AI. Upload your materials, 
          and let the system guide you through a personalized learning journey.
        </p>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {[
            { icon: '📊', title: 'Smart Roadmaps', desc: 'AI-generated learning paths based on your syllabus' },
            { icon: '🎯', title: 'Adaptive Learning', desc: 'Dynamically adjusts to your performance' },
            { icon: '📝', title: 'Auto Assessment', desc: 'AI-generated quizzes with instant feedback' },
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.2 }}
              className="card text-center"
            >
              <span className="text-3xl mb-3 block">{feature.icon}</span>
              <h3 className="text-lg font-semibold text-dark-100 mb-2">{feature.title}</h3>
              <p className="text-dark-400 text-sm">{feature.desc}</p>
            </motion.div>
          ))}
        </div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="flex gap-4 justify-center"
        >
          {isAuthenticated ? (
            <Link href="/dashboard" className="btn-primary text-lg px-8 py-3">
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link href="/auth" className="btn-primary text-lg px-8 py-3">
                Get Started
              </Link>
              <Link href="/auth" className="btn-secondary text-lg px-8 py-3">
                Sign In
              </Link>
            </>
          )}
        </motion.div>
      </motion.div>
    </main>
  );
}
