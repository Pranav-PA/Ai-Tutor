'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { authAPI } from '@/lib/api';
import { useAuthStore } from '@/store';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  });
  const router = useRouter();
  const { setUser, setToken } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const res = await authAPI.login({
          email: formData.email,
          password: formData.password,
        });
        setToken(res.data.access_token);
        
        // Get user info
        const userRes = await authAPI.getMe();
        setUser(userRes.data);
        
        toast.success('Welcome back!');
        router.push('/dashboard');
      } else {
        await authAPI.register(formData);
        toast.success('Account created! Please sign in.');
        setIsLogin(true);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-gradient-to-br from-dark-950 via-dark-900 to-primary-950 -z-10" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card w-full max-w-md"
      >
        <div className="text-center mb-8">
          <span className="text-4xl mb-4 block">🎓</span>
          <h1 className="text-2xl font-bold text-dark-50">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-dark-400 mt-2">
            {isLogin ? 'Sign in to continue learning' : 'Start your AI-powered learning journey'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">Full Name</label>
              <input
                type="text"
                className="input-field w-full"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                required={!isLogin}
                placeholder="John Doe"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-dark-300 mb-1">Email</label>
            <input
              type="email"
              className="input-field w-full"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-dark-300 mb-1">Password</label>
            <input
              type="password"
              className="input-field w-full"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              minLength={8}
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-3 text-center disabled:opacity-50"
          >
            {loading ? 'Loading...' : isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-primary-400 hover:text-primary-300 text-sm"
          >
            {isLogin ? "Don't have an account? Sign Up" : 'Already have an account? Sign In'}
          </button>
        </div>
      </motion.div>
    </main>
  );
}
