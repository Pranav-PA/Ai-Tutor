'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  Brain, Sparkles, BookOpen, GraduationCap, BarChart3,
  Zap, Clock, ArrowRight, Star, Upload, MessageSquare,
  Target, TrendingUp, Layers, FileText
} from 'lucide-react';

const features = [
  { icon: Brain, title: 'AI Multi-Agent System', desc: 'Specialized agents for teaching, quizzing, and revision that work together to accelerate your learning.', color: 'from-violet-500 to-purple-600' },
  { icon: BookOpen, title: 'Smart Document Parsing', desc: 'Upload PDFs, DOCX, slides, even handwritten notes. AI extracts and understands every detail.', color: 'from-blue-500 to-cyan-500' },
  { icon: Sparkles, title: 'RAG-Powered Accuracy', desc: 'Answers sourced directly from YOUR notes with context-aware retrieval. Zero hallucination.', color: 'from-amber-500 to-orange-500' },
  { icon: Target, title: 'Adaptive Quizzes', desc: 'AI-generated assessments that target weak areas and dynamically adjust difficulty.', color: 'from-emerald-500 to-green-600' },
  { icon: BarChart3, title: 'Learning Analytics', desc: 'Track progress with detailed insights, exam readiness scores, and study pattern analysis.', color: 'from-pink-500 to-rose-600' },
  { icon: Clock, title: 'Smart Study Planner', desc: 'Personalized schedules with spaced repetition optimized for your exam timeline.', color: 'from-indigo-500 to-blue-600' },
];

const steps = [
  { icon: Upload, title: 'Upload Materials', desc: 'Drop in your PDFs, notes, slides, and textbooks' },
  { icon: Brain, title: 'AI Processes Content', desc: 'Content is chunked, embedded, and indexed for RAG' },
  { icon: MessageSquare, title: 'Learn Interactively', desc: 'Ask questions, get taught, and take quizzes' },
  { icon: TrendingUp, title: 'Track & Improve', desc: 'See analytics, weak areas, and exam readiness' },
];

const stats = [
  { value: '10+', label: 'File Formats' },
  { value: 'AI', label: 'Powered RAG' },
  { value: '6', label: 'Smart Agents' },
  { value: '∞', label: 'Personalization' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Ambient Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,hsl(262,83%,58%,0.1),transparent)]" />
        <div className="absolute top-1/4 -left-20 w-[500px] h-[500px] rounded-full bg-violet-500/5 blur-[100px] animate-float" />
        <div className="absolute bottom-1/4 -right-20 w-[400px] h-[400px] rounded-full bg-indigo-500/5 blur-[100px] animate-float" style={{ animationDelay: '3s' }} />
      </div>

      {/* Navigation */}
      <header className="fixed top-0 w-full z-50">
        <div className="mx-4 mt-4">
          <nav className="container mx-auto px-6 py-3 rounded-2xl glass-strong shadow-lg shadow-black/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/25">
                  <GraduationCap className="w-5 h-5 text-white" />
                </div>
                <span className="font-display font-bold text-lg">SemesterAI</span>
              </div>
              <div className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
                <a href="#features" className="hover:text-foreground transition-colors">Features</a>
                <a href="#how-it-works" className="hover:text-foreground transition-colors">How it Works</a>
                <a href="#cta" className="hover:text-foreground transition-colors">Get Started</a>
              </div>
              <Link
                href="/dashboard"
                className="px-5 py-2.5 rounded-xl bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 transition-all shadow-lg shadow-primary/25 hover:shadow-primary/40"
              >
                Open App
              </Link>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-36 pb-24 px-6">
        <div className="container mx-auto text-center max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8 border border-primary/20">
              <Zap className="w-3.5 h-3.5" />
              <span>AI-Powered Learning Platform</span>
              <span className="px-2 py-0.5 rounded-full bg-primary/20 text-xs font-semibold">NEW</span>
            </div>
          </motion.div>

          <motion.h1
            className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-display font-bold mb-8 leading-[1.1] text-balance"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            Study Smarter with{' '}
            <span className="gradient-text">Your Personal</span>{' '}
            AI Tutor
          </motion.h1>

          <motion.p
            className="text-lg md:text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            Upload your notes and materials. Get personalized teaching, adaptive quizzes, smart revision plans, and exam prep — all powered by AI that learns YOUR content.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Link
              href="/dashboard"
              className="group inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold text-lg shadow-xl shadow-violet-500/25 hover:shadow-violet-500/40 hover:scale-[1.02] transition-all"
            >
              Start Learning Free
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <a
              href="#features"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl border-2 border-border text-foreground font-semibold text-lg hover:bg-muted/50 transition-all"
            >
              Explore Features
            </a>
          </motion.div>

          {/* Stats Row */}
          <motion.div
            className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-display font-bold text-foreground">{stat.value}</div>
                <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 px-6">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <p className="text-primary font-semibold text-sm uppercase tracking-wider mb-3">Features</p>
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-5 text-balance">
              Everything You Need to{' '}
              <span className="gradient-text">Ace Your Exams</span>
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              A complete AI study ecosystem that understands your course material and adapts to your unique learning style.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                className="group relative p-7 rounded-2xl bg-card border border-border hover:border-primary/20 transition-all duration-300 hover:shadow-xl hover:shadow-primary/5 hover:-translate-y-1"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-5 shadow-lg opacity-90 group-hover:opacity-100 group-hover:scale-110 transition-all`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-display font-semibold text-lg mb-2.5">{feature.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-24 px-6 relative">
        <div className="absolute inset-0 bg-muted/30" />
        <div className="container mx-auto max-w-5xl relative">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <p className="text-primary font-semibold text-sm uppercase tracking-wider mb-3">How It Works</p>
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-5">
              Four Simple Steps
            </h2>
            <p className="text-muted-foreground text-lg">From upload to mastery in minutes</p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                className="relative text-center p-6"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.12 }}
              >
                {/* Step number */}
                <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold shadow-lg shadow-primary/30">
                  {i + 1}
                </div>
                
                <div className="mt-6 w-16 h-16 rounded-2xl bg-card border border-border flex items-center justify-center mx-auto mb-4 shadow-sm">
                  <step.icon className="w-7 h-7 text-primary" />
                </div>
                <h3 className="font-display font-semibold text-base mb-2">{step.title}</h3>
                <p className="text-muted-foreground text-sm">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof / Capabilities */}
      <section className="py-24 px-6">
        <div className="container mx-auto max-w-5xl">
          <motion.div
            className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-600 p-12 md:p-16 text-white shadow-2xl shadow-violet-500/20"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            {/* Pattern overlay */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '32px 32px' }} />
            </div>
            
            <div className="relative grid md:grid-cols-2 gap-10 items-center">
              <div>
                <h2 className="text-3xl md:text-4xl font-display font-bold mb-4 leading-tight">
                  Built for Students Who Want to Excel
                </h2>
                <p className="text-white/80 text-lg leading-relaxed mb-6">
                  Whether you&apos;re preparing for finals, catching up on lectures, or mastering complex topics — our AI agents are here to help you understand, not just memorize.
                </p>
                <div className="flex flex-wrap gap-3">
                  {['PDF Notes', 'Slides', 'Handwritten', 'Textbooks', 'Papers'].map((tag) => (
                    <span key={tag} className="px-3 py-1.5 rounded-lg bg-white/15 text-sm font-medium backdrop-blur-sm border border-white/20">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { icon: Layers, label: 'Multi-Agent' },
                  { icon: FileText, label: 'RAG System' },
                  { icon: Target, label: 'Adaptive' },
                  { icon: Star, label: 'Personalized' },
                ].map((item) => (
                  <div key={item.label} className="p-5 rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20 text-center hover:bg-white/15 transition-colors">
                    <item.icon className="w-7 h-7 mx-auto mb-2 text-white/90" />
                    <span className="text-sm font-medium">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className="py-24 px-6">
        <div className="container mx-auto max-w-3xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-6 text-balance">
              Ready to Transform Your Studying?
            </h2>
            <p className="text-muted-foreground text-lg mb-10 max-w-xl mx-auto">
              Set up in seconds. Just add your API key and start learning smarter today — completely free and self-hosted.
            </p>
            <Link
              href="/dashboard"
              className="group inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-primary text-primary-foreground font-semibold text-lg shadow-xl shadow-primary/25 hover:shadow-primary/40 hover:scale-[1.02] transition-all"
            >
              Launch Dashboard
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-border">
        <div className="container mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
              <GraduationCap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-display font-semibold text-foreground">SemesterAI</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span>Built with</span>
            <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
            <span>for students everywhere</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
