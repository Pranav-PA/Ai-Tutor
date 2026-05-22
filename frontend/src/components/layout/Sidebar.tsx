'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/store';
import { 
  FiHome, FiBook, FiBarChart2, FiLogOut, FiUser 
} from 'react-icons/fi';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: FiHome },
  { href: '/learning', label: 'Learn', icon: FiBook },
  { href: '/quiz', label: 'Quiz', icon: FiBarChart2 },
  { href: '/analytics', label: 'Analytics', icon: FiBarChart2 },
];

export default function Sidebar({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <div className="flex h-screen bg-dark-950">
      {/* Sidebar */}
      <aside className="w-64 bg-dark-900 border-r border-dark-700 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-dark-700">
          <Link href="/dashboard" className="flex items-center gap-3">
            <span className="text-2xl">🎓</span>
            <span className="text-lg font-bold text-dark-50">AI Learning</span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-600/20 text-primary-400 border border-primary-600/30'
                    : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="absolute left-0 w-1 h-8 bg-primary-500 rounded-r"
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-dark-700">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
              <FiUser className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-dark-200 truncate">
                {user?.full_name || 'User'}
              </p>
              <p className="text-xs text-dark-500 truncate">
                {user?.email || ''}
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-2 text-dark-400 hover:text-red-400 text-sm w-full px-2 py-1 transition-colors"
          >
            <FiLogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
