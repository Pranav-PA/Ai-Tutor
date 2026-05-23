'use client';

import { ThemeProvider } from 'next-themes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useState, useEffect } from 'react';
import { UpdateNotification } from '@/components/UpdateNotification';
import { SetupWizard } from '@/components/SetupWizard';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 60 * 1000, retry: 1 },
        },
      })
  );

  const [showSetup, setShowSetup] = useState(false);

  useEffect(() => {
    // Show setup wizard on first run
    if (typeof window !== 'undefined') {
      const onboardingDone = localStorage.getItem('onboarding-complete');
      if (!onboardingDone) {
        setShowSetup(true);
      }
    }
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="dark" enableSystem themes={['light', 'dark', 'amoled']}>
        {showSetup && <SetupWizard onComplete={() => setShowSetup(false)} />}
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            className: 'bg-card text-card-foreground border border-border',
            style: {
              background: 'hsl(var(--card))',
              color: 'hsl(var(--card-foreground))',
              border: '1px solid hsl(var(--border))',
            },
          }}
        />
        <UpdateNotification />
      </ThemeProvider>
    </QueryClientProvider>
  );
}}
