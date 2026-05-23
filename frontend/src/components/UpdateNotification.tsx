'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, X, Sparkles } from 'lucide-react';

interface UpdateInfo {
  version: string;
  releaseDate?: string;
  releaseNotes?: string;
}

/**
 * Desktop-only component that shows update notifications.
 * Only renders when running inside Electron.
 */
export function UpdateNotification() {
  const [updateAvailable, setUpdateAvailable] = useState<UpdateInfo | null>(null);
  const [updateReady, setUpdateReady] = useState<UpdateInfo | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Only activate in Electron environment
    if (typeof window === 'undefined' || !window.electronAPI) return;

    window.electronAPI.onUpdateAvailable((info) => {
      setUpdateAvailable(info);
      setDismissed(false);
    });

    window.electronAPI.onUpdateDownloaded((info) => {
      setUpdateReady(info);
      setUpdateAvailable(null);
      setDismissed(false);
    });
  }, []);

  if (dismissed || (!updateAvailable && !updateReady)) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 50 }}
        className="fixed bottom-4 right-4 z-[100] max-w-sm"
      >
        <div className="bg-card border border-border rounded-2xl shadow-2xl p-4">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-primary/10">
              {updateReady ? (
                <Download className="w-5 h-5 text-primary" />
              ) : (
                <Sparkles className="w-5 h-5 text-primary" />
              )}
            </div>
            <div className="flex-1">
              <p className="font-semibold text-sm">
                {updateReady
                  ? `Update v${updateReady.version} ready!`
                  : `Update v${updateAvailable?.version} available`}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {updateReady
                  ? 'Restart the app to apply the update.'
                  : 'A new version is being downloaded...'}
              </p>
              {updateReady && (
                <button
                  onClick={() => window.electronAPI?.installUpdate()}
                  className="mt-2 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:opacity-90 transition-opacity"
                >
                  Restart & Update
                </button>
              )}
            </div>
            <button
              onClick={() => setDismissed(true)}
              className="p-1 rounded-lg hover:bg-secondary"
            >
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
